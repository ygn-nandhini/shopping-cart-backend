from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    price: float
    discount_percent: float = 0
    stock: int
    category_id: int


class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    discount_percent: float
    stock: int
    category_id: int

    class Config:
        from_attributes = True