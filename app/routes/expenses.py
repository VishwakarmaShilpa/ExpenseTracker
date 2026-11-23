from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Expense
from app.schemas import ExpenseCreate, ExpenseOut, ExpenseUpdate

router = APIRouter(prefix="/expenses", tags=["expenses"])


def get_or_404(db: Session, expense_id: int) -> Expense:
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.post("", response_model=ExpenseOut, status_code=201)
def create_expense(data: ExpenseCreate, db: Session = Depends(get_db)):
    expense = Expense(
        description=data.description,
        amount=data.amount,
        category=data.category or "Other",
        spent_on=data.spent_on,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("", response_model=list[ExpenseOut])
def list_expenses(
    category: str | None = None,
    start: date | None = None,
    end: date | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = select(Expense).order_by(Expense.spent_on.desc(), Expense.id.desc())
    if category:
        query = query.where(Expense.category == category)
    if start:
        query = query.where(Expense.spent_on >= start)
    if end:
        query = query.where(Expense.spent_on <= end)
    return db.scalars(query.limit(limit).offset(offset)).all()


@router.get("/{expense_id}", response_model=ExpenseOut)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, expense_id)


@router.patch("/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, data: ExpenseUpdate, db: Session = Depends(get_db)):
    expense = get_or_404(db, expense_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = get_or_404(db, expense_id)
    db.delete(expense)
    db.commit()
