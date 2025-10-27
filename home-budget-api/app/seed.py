from typing import Iterable
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import Category
from .db import SessionLocal

DEFAULT_CATEGORIES = ["food", "car", "accommodation", "gifts", "utilities", "entertainment"]

def _seed_categories_session(db: Session, names: Iterable[str]) -> int:
    created = 0
    for raw_name in names:
        name = (raw_name or "").strip()
        if not name:
            continue
        exists = (
            db.query(Category)
            .filter(func.lower(Category.name) == name.lower())
            .first()
        )
        if not exists:
            db.add(Category(name=name))
            created += 1
    if created:
        db.commit()
    return created

def seed_categories(names: Iterable[str] = None) -> int:
    items = list(names) if names else DEFAULT_CATEGORIES
    db = SessionLocal()
    try:
        return _seed_categories_session(db, items)
    finally:
        db.close()
