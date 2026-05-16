import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import delete as sa_delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Expense
from .schemas import ExpenseCreate, ExpenseUpdate


async def create_expense(session: AsyncSession, data: ExpenseCreate) -> Expense:
    expense = Expense(
        amount=data.amount,
        category=data.category,
        expense_date=data.expense_date,
        note=data.note,
    )
    session.add(expense)
    await session.commit()
    await session.refresh(expense)
    return expense


async def get_expense(session: AsyncSession, expense_id: uuid.UUID) -> Expense | None:
    result = await session.execute(select(Expense).where(Expense.id == expense_id))
    return result.scalar_one_or_none()


async def list_expenses(
    session: AsyncSession,
    category: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Expense], int, Decimal]:
    query = select(Expense)
    count_query = select(func.count(Expense.id))
    sum_query = select(func.coalesce(func.sum(Expense.amount), 0))

    if category is not None:
        query = query.where(Expense.category == category)
        count_query = count_query.where(Expense.category == category)
        sum_query = sum_query.where(Expense.category == category)
    if date_from is not None:
        query = query.where(Expense.expense_date >= date_from)
        count_query = count_query.where(Expense.expense_date >= date_from)
        sum_query = sum_query.where(Expense.expense_date >= date_from)
    if date_to is not None:
        query = query.where(Expense.expense_date <= date_to)
        count_query = count_query.where(Expense.expense_date <= date_to)
        sum_query = sum_query.where(Expense.expense_date <= date_to)

    query = query.order_by(Expense.expense_date.desc()).offset(skip).limit(limit)

    items_result = await session.execute(query)
    count_result = await session.execute(count_query)
    sum_result = await session.execute(sum_query)

    items = list(items_result.scalars().all())
    total = count_result.scalar_one()
    total_amount = sum_result.scalar_one() or Decimal("0")

    return items, total, Decimal(str(total_amount))


async def update_expense(
    session: AsyncSession, expense_id: uuid.UUID, data: ExpenseUpdate
) -> Expense | None:
    expense = await get_expense(session, expense_id)
    if expense is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)

    await session.commit()
    await session.refresh(expense)
    return expense


async def delete_expense(session: AsyncSession, expense_id: uuid.UUID) -> bool:
    result = await session.execute(sa_delete(Expense).where(Expense.id == expense_id))
    await session.commit()
    return result.rowcount > 0
