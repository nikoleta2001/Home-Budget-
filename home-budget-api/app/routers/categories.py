from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..models import Category
from ..schemas.category import CategoryCreate, CategoryOut
from ..auth.deps import get_db, get_current_user
from ..models import User

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    exists = db.query(Category).filter(Category.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Category already exists")
    cat = Category(name=payload.name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.get("", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Category).order_by(Category.name).all()

@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category Not Found")
    return cat

@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    cat.name = payload.name
    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return