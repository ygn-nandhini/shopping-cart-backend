from datetime import datetime
from pydantic import BaseModel


class OrderCreate(BaseModel):
    payment_method: str


class OrderUpdate(BaseModel):
    status: str


class OrderOut(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    created_at: datetime
    updated_at: datetime
    cancelled_by: int | None = None

    class Config:
        from_attributes = True

