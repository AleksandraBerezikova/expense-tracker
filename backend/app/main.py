import uuid
from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from . import crud
from .database import engine, get_session, init_db
from .schemas import (
    ExpenseCreate,
    ExpenseListResponse,
    ExpenseResponse,
    ExpenseUpdate,
    HealthResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(
    title="Expense Tracker API",
    description="RESTful service for personal expense tracking (single-user MVP)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.post(
    "/expenses",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new expense entry",
)
async def create_expense_endpoint(
    payload: ExpenseCreate,
    session: AsyncSession = Depends(get_session),
) -> ExpenseResponse:
    expense = await crud.create_expense(session, payload)
    return ExpenseResponse.model_validate(expense)


@app.get(
    "/expenses",
    response_model=ExpenseListResponse,
    summary="List expenses with optional filters",
)
async def list_expenses_endpoint(
    category: str | None = Query(default=None, max_length=64),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
) -> ExpenseListResponse:
    items, total, total_amount = await crud.list_expenses(
        session,
        category=category,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
    return ExpenseListResponse(
        total=total,
        total_amount=total_amount,
        items=[ExpenseResponse.model_validate(item) for item in items],
    )


@app.put(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse,
    summary="Update an existing expense entry",
)
async def update_expense_endpoint(
    expense_id: uuid.UUID,
    payload: ExpenseUpdate,
    session: AsyncSession = Depends(get_session),
) -> ExpenseResponse:
    expense = await crud.update_expense(session, expense_id, payload)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return ExpenseResponse.model_validate(expense)


@app.delete(
    "/expenses/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an expense entry",
)
async def delete_expense_endpoint(
    expense_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> Response:
    deleted = await crud.delete_expense(session, expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Service and database health check",
)
async def health_endpoint(session: AsyncSession = Depends(get_session)) -> HealthResponse:
    try:
        await session.execute(text("SELECT 1"))
        return HealthResponse(status="ok", database="ok")
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable")
    

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")