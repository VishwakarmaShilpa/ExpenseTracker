from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Budget, Expense
from app.schemas import CATEGORIES
from app.utils import month_range

router = APIRouter(prefix="/budgets", tags=["budgets"])


class BudgetIn(BaseModel):
    monthly_limit: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


def check_category(category: str):
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"category must be one of {CATEGORIES}")


@router.put("/{category}")
def set_budget(category: str, data: BudgetIn, db: Session = Depends(get_db)):
    check_category(category)
    budget = db.get(Budget, category)
    if budget:
        budget.monthly_limit = data.monthly_limit
    else:
        db.add(Budget(category=category, monthly_limit=data.monthly_limit))
    db.commit()
    return {"category": category, "monthly_limit": float(data.monthly_limit)}


@router.get("")
def list_budgets(db: Session = Depends(get_db)):
    budgets = db.scalars(select(Budget).order_by(Budget.category)).all()
    return [{"category": b.category, "monthly_limit": float(b.monthly_limit)} for b in budgets]


@router.delete("/{category}", status_code=204)
def delete_budget(category: str, db: Session = Depends(get_db)):
    budget = db.get(Budget, category)
    if budget is None:
        raise HTTPException(status_code=404, detail="No budget set for that category")
    db.delete(budget)
    db.commit()


@router.get("/status")
def budget_status(month: str = Query(..., description="Like 2026-11"), db: Session = Depends(get_db)):
    start, end = month_range(month)

    spent_rows = db.execute(
        select(Expense.category, func.sum(Expense.amount))
        .where(Expense.spent_on >= start, Expense.spent_on <= end)
        .group_by(Expense.category)
    ).all()
    spent_by_category = {cat: float(total) for cat, total in spent_rows}

    result = []
    for budget in db.scalars(select(Budget).order_by(Budget.category)).all():
        limit = float(budget.monthly_limit)
        spent = spent_by_category.get(budget.category, 0.0)
        percent = round(spent / limit * 100, 1)
        if percent >= 100:
            status = "over"
        elif percent >= 80:
            status = "warning"
        else:
            status = "ok"
        result.append({
            "category": budget.category,
            "limit": limit,
            "spent": round(spent, 2),
            "remaining": round(limit - spent, 2),
            "percent_used": percent,
            "status": status,
        })
    return {"month": month, "budgets": result}
