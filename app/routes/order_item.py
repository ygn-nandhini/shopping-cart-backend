from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order_item import OrderItem
from app.schemas.order_item import (
    OrderItemCreate,
    OrderItemUpdate,
    OrderItemOut
)
from app.auth.security import security
from app.auth.jwt import get_user_id_from_token
from app.services.audit_service import create_audit_log

router = APIRouter()


@router.post(
    "/order-items",
    response_model=OrderItemOut,
    dependencies=[Depends(security)]
)
def create_order_item(
    order_item: OrderItemCreate,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    new_order_item = OrderItem(
        order_id=order_item.order_id,
        product_id=order_item.product_id,
        quantity=order_item.quantity,
        price=order_item.price
    )

    db.add(new_order_item)
    db.commit()
    db.refresh(new_order_item)

    user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="CREATE",
        table_name="order_items",
        record_id=new_order_item.id,
        old_values=None,
        new_values={
            "order_id": new_order_item.order_id,
            "product_id": new_order_item.product_id,
            "quantity": new_order_item.quantity,
            "price": new_order_item.price
        }
    )
    db.commit()

    return new_order_item


@router.get(
    "/order-items",
    response_model=list[OrderItemOut],
    dependencies=[Depends(security)]
)
def get_order_items(
    db: Session = Depends(get_db)
):
    order_items = db.query(OrderItem).filter(
        OrderItem.is_deleted == False
    ).all()

    return order_items


@router.put(
    "/order-items/{order_item_id}",
    response_model=OrderItemOut,
    dependencies=[Depends(security)]
)
def update_order_item(
    order_item_id: int,
    order_item: OrderItemUpdate,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    existing_order_item = db.query(OrderItem).filter(
        OrderItem.id == order_item_id,
        OrderItem.is_deleted == False
    ).first()

    if not existing_order_item:
        return {"detail": "Order item not found"}

    old_values = {
        "quantity": existing_order_item.quantity,
        "price": existing_order_item.price
    }

    existing_order_item.quantity = order_item.quantity
    existing_order_item.price = order_item.price

    new_values = {
        "quantity": order_item.quantity,
        "price": order_item.price
    }

    db.commit()
    db.refresh(existing_order_item)

    user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        table_name="order_items",
        record_id=order_item_id,
        old_values=old_values,
        new_values=new_values
    )
    db.commit()

    return existing_order_item


@router.delete(
    "/order-items/{order_item_id}",
    dependencies=[Depends(security)]
)
def delete_order_item(
    order_item_id: int,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    existing_order_item = db.query(OrderItem).filter(
        OrderItem.id == order_item_id,
        OrderItem.is_deleted == False
    ).first()

    if not existing_order_item:
        return {"detail": "Order item not found"}

    old_values = {"is_deleted": existing_order_item.is_deleted}

    existing_order_item.is_deleted = True

    new_values = {"is_deleted": True}

    db.commit()
    db.refresh(existing_order_item)

    user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="DELETE",
        table_name="order_items",
        record_id=order_item_id,
        old_values=old_values,
        new_values=new_values
    )
    db.commit()

    return {"message": "Order item deleted successfully"}