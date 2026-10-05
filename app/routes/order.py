from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.schemas.order import OrderUpdate, OrderOut
from app.auth.security import security
from app.auth.jwt import get_user_id_from_token
from app.services.order_service import (
    create_order_from_cart,
    get_order_items_detail,
    cancel_order
)
from app.services.audit_service import create_audit_log

router = APIRouter()


@router.post(
    "/orders",
    response_model=OrderOut,
    dependencies=[Depends(security)]
)
def create_order(
    user_id: int,
    payment_method: str = "OTHER",
    db: Session = Depends(get_db)
):
    return create_order_from_cart(
        user_id,
        db,
        payment_method
    )


@router.get(
    "/orders",
    response_model=list[OrderOut],
    dependencies=[Depends(security)]
)
def get_orders(
    db: Session = Depends(get_db)
):
    orders = db.query(Order).filter(
        Order.is_deleted == False
    ).all()

    return orders


@router.get(
    "/orders/{order_id}/items",
    dependencies=[Depends(security)]
)
def order_items_detail(
    order_id: int,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    user_id = get_user_id_from_token(token.credentials)

    return get_order_items_detail(
        order_id,
        user_id,
        db
    )


@router.post(
    "/orders/{order_id}/cancel",
    response_model=OrderOut,
    dependencies=[Depends(security)]
)
def cancel_order_api(
    order_id: int,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    user_id = get_user_id_from_token(token.credentials)

    return cancel_order(
        order_id,
        user_id,
        db
    )


@router.put(
    "/orders/{order_id}",
    response_model=OrderOut,
    dependencies=[Depends(security)]
)
def update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    existing_order = db.query(Order).filter(
        Order.id == order_id,
        Order.is_deleted == False
    ).first()

    if not existing_order:
        return {"detail": "Order not found"}

    old_values = {
        "status": existing_order.status
    }

    existing_order.status = order.status

    new_values = {
        "status": order.status
    }

    db.commit()
    db.refresh(existing_order)

    user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        table_name="orders",
        record_id=order_id,
        old_values=old_values,
        new_values=new_values
    )

    db.commit()

    return existing_order


@router.delete(
    "/orders/{order_id}",
    dependencies=[Depends(security)]
)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    existing_order = db.query(Order).filter(
        Order.id == order_id,
        Order.is_deleted == False
    ).first()

    if not existing_order:
        return {"detail": "Order not found"}

    old_values = {
        "is_deleted": existing_order.is_deleted
    }

    existing_order.is_deleted = True

    new_values = {
        "is_deleted": True
    }

    db.commit()
    db.refresh(existing_order)

    user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="DELETE",
        table_name="orders",
        record_id=order_id,
        old_values=old_values,
        new_values=new_values
    )

    db.commit()

    return {
        "message": "Order deleted successfully"
    }

