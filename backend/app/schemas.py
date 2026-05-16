import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ExpenseBase(BaseModel):
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    category: str = Field(..., min_length=1, max_length=64)
    expense_date: date
    note: str | None = Field(default=None, max_length=1000)


class ExpenseCreate(ExpenseBase):
    """"""


class ExpenseUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    category: str | None = Field(default=None, min_length=1, max_length=64)
    expense_date: date | None = None
    note: str | None = Field(default=None, max_length=1000)


class ExpenseResponse(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ExpenseListResponse(BaseModel):
    total: int
    total_amount: Decimal
    items: list[ExpenseResponse]


class HealthResponse(BaseModel):
    status: str
    database: str
