from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, DateTime, Numeric
from datetime import datetime
from .base import Base

class Expense(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id", ondelete="SET NULL"), nullable=True, index=True)
    description: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")
