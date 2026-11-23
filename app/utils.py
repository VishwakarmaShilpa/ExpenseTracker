from calendar import monthrange
from datetime import date

from fastapi import HTTPException


def month_range(month: str):
    """'2026-11' -> (first day, last day) of that month."""
    try:
        year, mon = (int(part) for part in month.split("-"))
        start = date(year, mon, 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="month must look like 2026-11")
    end = date(year, mon, monthrange(year, mon)[1])
    return start, end


def previous_month_range(start: date):
    if start.month == 1:
        prev_start = date(start.year - 1, 12, 1)
    else:
        prev_start = date(start.year, start.month - 1, 1)
    prev_end = date(prev_start.year, prev_start.month, monthrange(prev_start.year, prev_start.month)[1])
    return prev_start, prev_end
