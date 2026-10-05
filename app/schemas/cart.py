from pydantic import BaseModel
class CartCreate(BaseModel):
    user_id: int


class CartOut(BaseModel):
    id: int
    user_id: int

    class Config:
        from_attributes = True