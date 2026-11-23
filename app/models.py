from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import String, Date, DateTime, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


def now():
    return datetime.now(timezone.utc)


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    category: Mapped[str] = mapped_column(String(50), index=True)
    spent_on: Mapped[date] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Budget(Base):
    __tablename__ = "budgets"

    category: Mapped[str] = mapped_column(String(50), primary_key=True)
    monthly_limit: Mapped[Decimal] = mapped_column(Numeric(10, 2))
