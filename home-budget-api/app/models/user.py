from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float
from .base import Base

class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    balance: Mapped[float] = mapped_column(Float, default=0.0)

    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")