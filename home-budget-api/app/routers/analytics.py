from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from ..auth.deps import get_db, get_current_user
from ..models import Expense, Category, User, Income

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _start_of_month(dt: datetime) -> datetime:
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def _end_of_month(dt: datetime) -> datetime:
    first_next = (dt.replace(day=1) + timedelta(days=32)).replace(day=1)
    return first_next.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)

def _quarter_bounds(dt: datetime) -> (datetime, datetime):
    q = (dt.month - 1) // 3 + 1
    start_month = 3 * (q - 1) + 1
    start = dt.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
    end_month_first = (start.replace(day=1) + timedelta(days=92)).replace(day=1)  # enough to jump next quarter
    end = end_month_first - timedelta(microseconds=1)
    return start, end

def _period_range(period: Optional[str], date_from: Optional[datetime], date_to: Optional[datetime]) -> (datetime, datetime, str):
    if date_from and date_to:
        if date_to.hour == 0 and date_to.minute == 0 and date_to.second == 0 and date_to.microsecond == 0:
            date_to = date_to.replace(hour=23, minute=59, second=59, microsecond=999999)
        return date_from, date_to, "custom"

    if (date_from and not date_to) or (date_to and not date_from):
        raise HTTPException(status_code=400, detail="Provide both date_from and date_to, or use 'period'")

    now = datetime.now(timezone.utc)
    today = now.astimezone(timezone.utc)

    p = (period or "last_month").lower()

    if p == "this_month":
        start = _start_of_month(today)
        end = _end_of_month(today)
        return start, end, p
    elif p == "last_month":
        first_this = _start_of_month(today)
        last_month_end = first_this - timedelta(microseconds=1)
        start = _start_of_month(last_month_end)
        end = _end_of_month(last_month_end)
        return start, end, p
    elif p == "this_quarter":
        start, end = _quarter_bounds(today)
        return start, end, p
    elif p == "last_quarter":
        start_this, _ = _quarter_bounds(today)
        last_q_end = start_this - timedelta(microseconds=1)
        start, end = _quarter_bounds(last_q_end)
        return start, end, p
    elif p == "this_year":
        start = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = today.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        return start, end, p
    elif p == "last_year":
        start = today.replace(year=today.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = today.replace(year=today.year - 1, month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        return start, end, p
    else:
        raise HTTPException(status_code=400, detail="Invalid 'period'. Use one of: this_month, last_month, this_quarter, last_quarter, this_year, last_year, or provide date_from & date_to")


@router.get("/summary")
def analytics_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    period: Optional[str] = Query(None, description="this_month | last_month | this_quarter | last_quarter | this_year | last_year"),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
) -> Dict[str, Any]:
    start, end, period_name = _period_range(period, date_from, date_to)

    q = db.query(Expense).filter(Expense.user_id == user.id, Expense.created_at >= start, Expense.created_at <= end)

    spent_total = db.query(func.coalesce(func.sum(Expense.amount), 0.0))\
        .filter(Expense.user_id == user.id, Expense.created_at >= start, Expense.created_at <= end)\
        .scalar() or 0.0

    count_total = db.query(func.count(Expense.id))\
        .filter(Expense.user_id == user.id, Expense.created_at >= start, Expense.created_at <= end)\
        .scalar() or 0

    cat_label = func.coalesce(Category.name, 'uncategorized')
    by_cat_rows = (
        db.query(cat_label.label("category"), func.coalesce(func.sum(Expense.amount), 0.0).label("total"))
        .outerjoin(Category, Expense.category_id == Category.id)
        .filter(Expense.user_id == user.id, Expense.created_at >= start, Expense.created_at <= end)
        .group_by(cat_label)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )
    by_category = [{"category": r.category, "total": float(r.total)} for r in by_cat_rows]

    lifetime_spent = db.query(func.coalesce(func.sum(Expense.amount), 0.0))\
        .filter(Expense.user_id == user.id)\
        .scalar() or 0.0
    
    by_source_rows = (
    db.query(Income.description.label("source"),
             func.coalesce(func.sum(Income.amount), 0.0).label("total"))
    .filter(Income.user_id == user.id,
            Income.created_at >= start,
            Income.created_at <= end)
    .group_by(Income.description)
    .order_by(func.sum(Income.amount).desc())
    .all()
    )
    by_source = [{"source": r.source, "total": float(r.total)} for r in by_source_rows]

    earned_total = db.query(func.coalesce(func.sum(Income.amount), 0.0))\
        .filter(Income.user_id == user.id, Income.created_at >= start, Income.created_at <= end)\
        .scalar() or 0.0

    lifetime_earned = db.query(func.coalesce(func.sum(Income.amount), 0.0))\
        .filter(Income.user_id == user.id)\
        .scalar() or 0.0

    net_total = float(earned_total) - float(spent_total)
    initial_estimate = float(user.balance or 0.0) + float(lifetime_spent) - float(lifetime_earned)

    
    return {
        "period": {
            "name": period_name,
            "from": start.isoformat(),
            "to": end.isoformat()
        },
        "totals": {
            "earned": float(earned_total),
            "spent": float(spent_total),
            "net": float(net_total),
            "count_expenses": int(count_total),
        },
        "by_category": by_category,   
        "by_source": by_source,       
        "account": {
            "current_balance": float(user.balance or 0.0),
            "initial_estimate": float(initial_estimate),
            "lifetime_spent": float(lifetime_spent),
            "lifetime_earned": float(lifetime_earned),
        },
    }
