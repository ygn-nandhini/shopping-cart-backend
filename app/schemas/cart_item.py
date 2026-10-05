from pydantic import BaseModel


class CartItemCreate(BaseModel):
    cart_id: int
    product_id: int
    quantity: int


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemOut(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True