from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cart_item import CartItem
from app.schemas.cart_item import (
    CartItemCreate,
    CartItemUpdate,
    CartItemOut
)
from app.auth.jwt import get_user_id_from_token
from app.services.audit_service import create_audit_log

router = APIRouter()

security = HTTPBearer()


@router.post(
    "/cart-items",
    response_model=CartItemOut,
    dependencies=[Depends(security)]
)
def create_cart_item(
    cart_item: CartItemCreate,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    new_cart_item = CartItem(
        cart_id=cart_item.cart_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity
    )

    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)

    user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="CREATE",
        table_name="cart_items",
        record_id=new_cart_item.id,
        old_values=None,
        new_values={
            "cart_id": new_cart_item.cart_id,
            "product_id": new_cart_item.product_id,
            "quantity": new_cart_item.quantity
        }
    )
    db.commit()

    return new_cart_item


@router.get(
    "/cart-items",
    response_model=list[CartItemOut],
    dependencies=[Depends(security)]
)
def get_cart_items(
    db: Session = Depends(get_db)
):
    cart_items = db.query(CartItem).filter(
        CartItem.is_deleted == False
    ).all()

    return cart_items


@router.put(
    "/cart-items/{cart_item_id}",
    response_model=CartItemOut,
    dependencies=[Depends(security)]
)
def update_cart_item(
    cart_item_id: int,
    cart_item: CartItemUpdate,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    existing_cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.is_deleted == False
    ).first()

    if not existing_cart_item:
        return {"detail": "Cart item not found"}

    old_values = {"quantity": existing_cart_item.quantity}

    existing_cart_item.quantity = cart_item.quantity

    new_values = {"quantity": cart_item.quantity}

    db.commit()
    db.refresh(existing_cart_item)

    user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        table_name="cart_items",
        record_id=cart_item_id,
        old_values=old_values,
        new_values=new_values
    )
    db.commit()

    return existing_cart_item


@router.delete(
    "/cart-items/{cart_item_id}",
    dependencies=[Depends(security)]
)
def delete_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    existing_cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.is_deleted == False
    ).first()

    if not existing_cart_item:
        return {"detail": "Cart item not found"}

    old_values = {"is_deleted": existing_cart_item.is_deleted}

    existing_cart_item.is_deleted = True

    new_values = {"is_deleted": True}

    db.commit()
    db.refresh(existing_cart_item)

    user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="DELETE",
        table_name="cart_items",
        record_id=cart_item_id,
        old_values=old_values,
        new_values=new_values
    )
    db.commit()

    return {"message": "Cart item deleted successfully"}