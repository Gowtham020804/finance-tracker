from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    password: str


class Expense(BaseModel):
    username: str
    amount: float
    category: str
    description: Optional[str] = ""
    date: str
