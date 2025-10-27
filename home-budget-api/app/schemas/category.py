from pydantic import BaseModel, ConfigDict

class CategoryBase(BaseModel):
    name: str

    model_config = {
        "json_schema_extra": {
            "example": {"name": "food"}
        }
    }

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
