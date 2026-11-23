from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

CATEGORIES = [
    "Food", "Transport", "Shopping", "Bills",
    "Entertainment", "Health", "Education", "Other",
]


def _check_category(value: str) -> str:
    if value not in CATEGORIES:
        raise ValueError(f"category must be one of {CATEGORIES}")
    return value


Category = Annotated[str, AfterValidator(_check_category)]


class ExpenseCreate(BaseModel):
    description: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category: Category | None = None  # Step 4 fills this in automatically
    spent_on: date


class ExpenseUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=255)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    category: Category | None = None
    spent_on: date | None = None


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    amount: float
    category: str
    spent_on: date
