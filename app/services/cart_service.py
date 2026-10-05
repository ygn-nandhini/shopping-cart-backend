from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product


def get_cart_summary(user_id: int, db: Session):
    cart = db.query(Cart).filter(
        Cart.user_id == user_id,
        Cart.is_deleted == False
    ).first()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart_items = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.is_deleted == False
    ).all()

    items_list = []
    total_amount = 0

    for item in cart_items:
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.is_deleted == False
        ).first()

        if not product:
            continue

        discount_amount = (
            product.price * product.discount_percent / 100
        )
        discounted_price = product.price - discount_amount
        subtotal = discounted_price * item.quantity
        total_amount += subtotal

        items_list.append({
            "cart_item_id": item.id,
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "discount_percent": product.discount_percent,
            "discounted_price": discounted_price,
            "quantity": item.quantity,
            "subtotal": subtotal
        })

    return {
        "cart_id": cart.id,
        "items": items_list,
        "total_amount": total_amount
    }