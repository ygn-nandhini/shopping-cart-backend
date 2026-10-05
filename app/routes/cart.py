from app.auth.jwt import get_user_id_from_token
from app.services.audit_service import create_audit_log
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cart import Cart
from app.schemas.cart import CartCreate, CartOut
from app.services.cart_service import get_cart_summary

router = APIRouter()

security = HTTPBearer()


@router.post(
    "/cart",
    response_model=CartOut,
    dependencies=[Depends(security)]
)
def create_cart(
    cart: CartCreate,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    new_cart = Cart(
        user_id=cart.user_id
    )
    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)
    user_id = get_user_id_from_token(token.credentials)
    create_audit_log(
        db=db,
        user_id=user_id,
        action="CREATE",
        table_name="cart",
        record_id=new_cart.id,
        old_values=None,
        new_values={"user_id": new_cart.user_id}
    )
    db.commit()
    return new_cart


@router.get(
    "/cart",
    response_model=list[CartOut],
    dependencies=[Depends(security)]
)
def get_carts(
    db: Session = Depends(get_db)
):
    carts = db.query(Cart).filter(
        Cart.is_deleted == False
    ).all()

    return carts


@router.get(
    "/cart-summary",
    dependencies=[Depends(security)]
)
def cart_summary(
    user_id: int,
    db: Session = Depends(get_db)
):
    return get_cart_summary(user_id, db)


@router.delete(
    "/cart/{cart_id}",
    dependencies=[Depends(security)]
)
def delete_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    existing_cart = db.query(Cart).filter(
        Cart.id == cart_id,
        Cart.is_deleted == False
    ).first()

    if not existing_cart:
        return {"detail": "Cart not found"}

    old_values = {"is_deleted": existing_cart.is_deleted}

    existing_cart.is_deleted = True

    new_values = {"is_deleted": True}

    db.commit()
    db.refresh(existing_cart)

    user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="DELETE",
        table_name="cart",
        record_id=cart_id,
        old_values=old_values,
        new_values=new_values
    )
    db.commit()

    return {"message": "Cart deleted successfully"}