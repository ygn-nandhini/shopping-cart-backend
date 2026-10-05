from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate


def create_product(product: ProductCreate, db: Session):
    new_product = Product(
        name=product.name,
        price=product.price,
        discount_percent=product.discount_percent,
        stock=product.stock,
        category_id=product.category_id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def set_overall_discount(discount_percent: float, db: Session):
    products = db.query(Product).filter(Product.is_deleted == False).all()
    for product in products:
        product.discount_percent = discount_percent
    db.commit()
    return {
        "message": f"Applied {discount_percent}% discount to {len(products)} products"
    }