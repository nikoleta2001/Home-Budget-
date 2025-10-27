from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

    model_config = {
        "json_schema_extra": {
            "example": {"email": "user@example.com", "password": "secret123"}
        }
    }

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginIn(BaseModel):
    username: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {"username": "user@example.com", "password": "secret123"}
        }
    }
