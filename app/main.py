from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401
from app.routes import auth, budgets, expenses, reports

load_dotenv()

app = FastAPI(title="Smart Expense Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(expenses.router)
app.include_router(reports.router)
app.include_router(budgets.router)
app.include_router(auth.router)


@app.get("/")
def health():
    return {"status": "ok"}