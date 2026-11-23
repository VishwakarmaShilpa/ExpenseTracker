from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (registers the tables)
from app.database import Base, engine
from app.routes import budgets, expenses, reports

app = FastAPI(title="Smart Expense Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)  # creates any missing tables
app.include_router(expenses.router)
app.include_router(reports.router)
app.include_router(budgets.router)


@app.get("/")
def health():
    return {"status": "ok"}
