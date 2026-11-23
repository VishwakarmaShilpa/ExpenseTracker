from calendar import monthrange
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Expense
from app.utils import month_range, previous_month_range

router = APIRouter(prefix="/reports", tags=["reports"])


def total_between(db: Session, start: date, end: date) -> float:
    value = db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0))
        .where(Expense.spent_on >= start, Expense.spent_on <= end)
    )
    return float(value)


@router.get("/monthly")
def monthly_report(month: str = Query(..., description="Like 2026-11"), db: Session = Depends(get_db)):
    start, end = month_range(month)
    total = total_between(db, start, end)

    category_rows = db.execute(
        select(Expense.category, func.sum(Expense.amount), func.count())
        .where(Expense.spent_on >= start, Expense.spent_on <= end)
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
    ).all()
    by_category = [
        {
            "category": cat,
            "total": float(amount),
            "count": count,
            "share_percent": round(float(amount) / total * 100, 1) if total else 0.0,
        }
        for cat, amount, count in category_rows
    ]

    daily_rows = db.execute(
        select(Expense.spent_on, func.sum(Expense.amount))
        .where(Expense.spent_on >= start, Expense.spent_on <= end)
        .group_by(Expense.spent_on)
        .order_by(Expense.spent_on)
    ).all()
    daily = [{"date": d.isoformat(), "total": float(t)} for d, t in daily_rows]

    top_rows = db.scalars(
        select(Expense)
        .where(Expense.spent_on >= start, Expense.spent_on <= end)
        .order_by(Expense.amount.desc())
        .limit(5)
    ).all()
    top_expenses = [
        {
            "id": e.id,
            "description": e.description,
            "amount": float(e.amount),
            "category": e.category,
            "date": e.spent_on.isoformat(),
        }
        for e in top_rows
    ]

    prev_start, prev_end = previous_month_range(start)
    prev_total = total_between(db, prev_start, prev_end)
    change_percent = None if prev_total == 0 else round((total - prev_total) / prev_total * 100, 1)

    projected = None
    today = date.today()
    if start <= today <= end:
        days_in_month = monthrange(start.year, start.month)[1]
        projected = round(total / today.day * days_in_month, 2)

    return {
        "month": month,
        "total": round(total, 2),
        "previous_month_total": round(prev_total, 2),
        "change_vs_previous_percent": change_percent,
        "projected_month_end": projected,
        "by_category": by_category,
        "daily": daily,
        "top_expenses": top_expenses,
    }
