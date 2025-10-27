from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=6)

class UserOut(UserBase):
    id: int
    balance: float

    class Config:
        from_attributes = True
