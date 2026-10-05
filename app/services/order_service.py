from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.services.audit_service import create_audit_log


def create_order_from_cart(
    user_id: int,
    db: Session,
    payment_method: str = "OTHER"
):
    cart = db.query(Cart).filter(
        Cart.user_id == user_id,
        Cart.is_deleted == False
    ).first()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    cart_items = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.is_deleted == False
    ).all()

    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    # Calculate product-discounted cart total
    total_amount = 0

    for item in cart_items:
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.is_deleted == False
        ).first()

        if not product:
            item.is_deleted = True
            continue

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}"
            )

        discount_amount = (
            product.price * product.discount_percent / 100
        )

        discounted_price = (
            product.price - discount_amount
        )

        total_amount += (
            discounted_price * item.quantity
        )

    
    # EXTRA CART OFFER
    # ₹3000 or more -> 10% extra discount
    cart_offer_discount = 0

    if total_amount >= 3000:
        cart_offer_discount = total_amount * 10 / 100
        total_amount -= cart_offer_discount

    # CREDIT CARD OFFER
    # Credit Card -> 5% extra discount
    credit_card_discount = 0
    if payment_method == "CREDIT_CARD":
        credit_card_discount = total_amount * 5 / 100
        total_amount -= credit_card_discount

    # Create order
    new_order = Order(
        user_id=user_id,
        total_amount=total_amount,
        status="PENDING"
    )

    db.add(new_order)
    db.flush()

    # Create order items
    for item in cart_items:
        if item.is_deleted:
            continue

        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.is_deleted == False
        ).first()

        discount_amount = (
            product.price * product.discount_percent / 100
        )

        discounted_price = (
            product.price - discount_amount
        )

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=discounted_price
        )

        db.add(order_item)

        product.stock -= item.quantity
        item.is_deleted = True

    db.commit()
    db.refresh(new_order)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="CREATE",
        table_name="orders",
        record_id=new_order.id,
        old_values=None,
        new_values={
            "total_amount": new_order.total_amount,
            "status": new_order.status
        }
    )

    db.commit()

    return new_order


def get_order_items_detail(
    order_id: int,
    user_id: int,
    db: Session
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.is_deleted == False
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not your order"
        )

    rows = db.query(OrderItem, Product).join(
        Product,
        Product.id == OrderItem.product_id
    ).filter(
        OrderItem.order_id == order_id,
        OrderItem.is_deleted == False
    ).all()

    return [
        {
            "product_name": product.name,
            "price": item.price,
            "quantity": item.quantity,
            "subtotal": item.price * item.quantity
        }
        for item, product in rows
    ]


def cancel_order(
    order_id: int,
    user_id: int,
    db: Session
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.is_deleted == False
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not your order"
        )

    if order.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Only PENDING orders can be cancelled"
        )

    items = db.query(OrderItem).filter(
        OrderItem.order_id == order_id,
        OrderItem.is_deleted == False
    ).all()

    for item in items:
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if product:
            product.stock += item.quantity

    old_values = {
        "status": order.status
    }

    order.status = "CANCELLED"
    order.cancelled_by = user_id

    create_audit_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        table_name="orders",
        record_id=order.id,
        old_values=old_values,
        new_values={
            "status": "CANCELLED",
            "cancelled_by": user_id
        }
    )

    db.commit()
    db.refresh(order)

    return order
