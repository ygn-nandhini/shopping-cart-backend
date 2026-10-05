from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product import ProductCreate, ProductOut
from app.models.product import Product
from app.services.product_service import create_product, set_overall_discount
from app.auth.jwt import get_user_id_from_token
from app.services.audit_service import create_audit_log


router = APIRouter()

security = HTTPBearer()


@router.post(
    "/products",
    response_model=ProductOut,
    dependencies=[Depends(security)]
)
def create_product_api(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    return create_product(product, db)


@router.get(
    "/products",
    response_model=list[ProductOut],
    dependencies=[Depends(security)]
)
def get_products(
    db: Session = Depends(get_db)
):
    products = db.query(Product).filter(
        Product.is_deleted == False
    ).all()

    return products


@router.put(
    "/products/overall-discount",
    dependencies=[Depends(security)]
)
def apply_overall_discount(
    discount_percent: float,
    db: Session = Depends(get_db)
):
    return set_overall_discount(discount_percent, db)


@router.put(
    "/products/{product_id}",
    response_model=ProductOut,
    dependencies=[Depends(security)]
)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    existing_product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_deleted == False
    ).first()

    if not existing_product:
        return {"detail": "Product not found"}


    old_values = {
        "name": existing_product.name,
        "price": existing_product.price,
        "discount_percent": existing_product.discount_percent,
        "stock": existing_product.stock,
        "category_id": existing_product.category_id
    }

    existing_product.name = product.name
    existing_product.price = product.price
    existing_product.discount_percent = product.discount_percent
    existing_product.stock = product.stock
    existing_product.category_id = product.category_id

    new_values = {
        "name": product.name,
        "price": product.price,
        "discount_percent": product.discount_percent,
        "stock": product.stock,
        "category_id": product.category_id
    }

    user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        table_name="products",
        record_id=product_id,
        old_values=old_values,
        new_values=new_values
    )

    db.commit()
    db.refresh(existing_product)

    return existing_product


@router.delete(
    "/products/{product_id}",
    dependencies=[Depends(security)]
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    existing_product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_deleted == False
    ).first()

    if not existing_product:
        return {"detail": "Product not found"}

    old_values = {"is_deleted": existing_product.is_deleted}

    existing_product.is_deleted = True

    new_values = {"is_deleted": True}

    user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="DELETE",
        table_name="products",
        record_id=product_id,
        old_values=old_values,
        new_values=new_values
    )

    db.commit()
    db.refresh(existing_product)

    return {"message": "Product deleted successfully"}