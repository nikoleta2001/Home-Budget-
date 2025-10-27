from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime, UTC
from ..models import Expense, Category, User
from ..schemas.expense import ExpenseCreate, ExpenseOut
from ..auth.deps import get_db, get_current_user

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.post("", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    category = None
    if payload.category_id is not None:
        category = db.get(Category, payload.category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category_id")

    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    user.balance = (user.balance or 0) - float(payload.amount)

    expense = Expense(
        user_id=user.id,
        category_id=payload.category_id,
        description=payload.description,
        amount=float(payload.amount),
        created_at=datetime.now(UTC),
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    expense.category = category
    return expense

@router.get("", response_model=List[ExpenseOut])
def list_expenses(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    category_id: Optional[int] = None,
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    date_from: Optional[datetime] = Query(None, description="ISO format, npr. 2025-01-31T00:00:00"),
    date_to: Optional[datetime] = Query(None, description="ISO format, npr. 2025-02-28T23:59:59"),
):
    q = db.query(Expense).filter(Expense.user_id == user.id)

    if category_id is not None:
        q = q.filter(Expense.category_id == category_id)
    if amount_min is not None:
        q = q.filter(Expense.amount >= amount_min)
    if amount_max is not None:
        q = q.filter(Expense.amount <= amount_max)
    if date_from is not None:
        q = q.filter(Expense.created_at >= date_from)
    if date_to is not None:
        q = q.filter(Expense.created_at <= date_to)

    items = q.order_by(Expense.created_at.desc()).all()
    for e in items:
        if e.category_id:
            e.category = db.get(Category, e.category_id)
    return items

@router.get("/{expense_id}", response_model=ExpenseOut)
def get_expense(expense_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    e = db.get(Expense, expense_id)
    if not e or e.user_id != user.id:
        raise HTTPException(status_code=404, detail="Expense not found")
    if e.category_id:
        e.category = db.get(Category, e.category_id)
    return e

@router.put("/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, payload: ExpenseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    e = db.get(Expense, expense_id)
    if not e or e.user_id != user.id:
        raise HTTPException(status_code=404, detail="Expense not found")

    user.balance = (user.balance or 0) + float(e.amount) - float(payload.amount)

    if payload.category_id is not None:
        if not db.get(Category, payload.category_id):
            raise HTTPException(status_code=400, detail="Invalid category_id")

    e.description = payload.description
    e.amount = float(payload.amount)
    e.category_id = payload.category_id
    db.commit()
    db.refresh(e)
    if e.category_id:
        e.category = db.get(Category, e.category_id)
    return e

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    e = db.get(Expense, expense_id)
    if not e or e.user_id != user.id:
        raise HTTPException(status_code=404, detail="Expense not found")

    user.balance = (user.balance or 0) + float(e.amount)
    db.delete(e)
    db.commit()
    return
