from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, UTC
from ..auth.deps import get_db, get_current_user
from ..models import Income, User
from ..schemas.income import IncomeCreate, IncomeOut

router = APIRouter(prefix="/incomes", tags=["incomes"])

@router.post("", response_model=IncomeOut, status_code=status.HTTP_201_CREATED)
def create_income(
    payload: IncomeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    income = Income(
        user_id=user.id,
        description=payload.description,
        amount=float(payload.amount),
        created_at=datetime.now(UTC),
    )
    user.balance = (user.balance or 0.0) + float(payload.amount)

    db.add(income)
    db.commit()
    db.refresh(income)
    return income

@router.get("", response_model=List[IncomeOut])
def list_incomes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    date_from: Optional[datetime] = Query(None, description="ISO, npr. 2025-01-01T00:00:00Z"),
    date_to: Optional[datetime] = Query(None, description="ISO, npr. 2025-12-31T23:59:59Z"),
):
    q = db.query(Income).filter(Income.user_id == user.id)
    if amount_min is not None:
        q = q.filter(Income.amount >= amount_min)
    if amount_max is not None:
        q = q.filter(Income.amount <= amount_max)
    if date_from is not None:
        q = q.filter(Income.created_at >= date_from)
    if date_to is not None:
        q = q.filter(Income.created_at <= date_to)
    return q.order_by(Income.created_at.desc()).all()

@router.get("/{income_id}", response_model=IncomeOut)
def get_income(income_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    inc = db.get(Income, income_id)
    if not inc or inc.user_id != user.id:
        raise HTTPException(status_code=404, detail="Income not found")
    return inc

@router.put("/{income_id}", response_model=IncomeOut)
def update_income(
    income_id: int,
    payload: IncomeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inc = db.get(Income, income_id)
    if not inc or inc.user_id != user.id:
        raise HTTPException(status_code=404, detail="Income not found")
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    user.balance = (user.balance or 0.0) - float(inc.amount) + float(payload.amount)

    inc.description = payload.description
    inc.amount = float(payload.amount)
    db.commit()
    db.refresh(inc)
    return inc

@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(income_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    inc = db.get(Income, income_id)
    if not inc or inc.user_id != user.id:
        raise HTTPException(status_code=404, detail="Income not found")

    user.balance = (user.balance or 0.0) - float(inc.amount)
    db.delete(inc)
    db.commit()
    return
