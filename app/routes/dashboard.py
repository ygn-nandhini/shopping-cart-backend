from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy import func

from app.database import SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.category import Category
router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/summary", dependencies=[Depends(HTTPBearer())])
def get_dashboard_summary():
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        total_products = db.query(Product).filter(
            Product.is_deleted == False
        ).count()
        total_orders = db.query(Order).count()

        total_order_amount = db.query(
            func.sum(Order.total_amount)
        ).scalar() or 0

        return {
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_order_amount": total_order_amount
        }

    finally:
        db.close()


@router.get("/recent-orders", dependencies=[Depends(HTTPBearer())])
def get_recent_orders():
    db = SessionLocal()
    try:
        recent_orders = (
            db.query(Order)
            .order_by(Order.created_at.desc())
            .limit(5)
            .all()
        )
        return [
            {
                "id": order.id,
                "user_id": order.user_id,
                "total_amount": order.total_amount,
                "status": order.status,
                "created_at": order.created_at
            }
            for order in recent_orders
        ]

    finally:
        db.close()

@router.get("/product-stock", dependencies=[Depends(HTTPBearer())])
def get_product_stock():

    db = SessionLocal()

    try:
        products = (
            db.query(Product)
            .filter(Product.is_deleted == False)
            .order_by(Product.stock.asc())
            .limit(5)
            .all()
        )

        return [
            {
                "id": product.id,
                "name": product.name,
                "stock": product.stock
            }
            for product in products
        ]

    finally:
        db.close()

@router.get("/order-status", dependencies=[Depends(HTTPBearer())])
def get_order_status():

    db = SessionLocal()

    try:
        order_status = (
            db.query(
                func.upper(Order.status).label("status"),
                func.count(Order.id).label("count")
            )
            .group_by(func.upper(Order.status))
            .all()
        )

        return [
            {
                "status": status,
                "count": count
            }
            for status, count in order_status
        ]

    finally:
        db.close()

@router.get("/category-products", dependencies=[Depends(HTTPBearer())])
def get_category_product_count():

    db = SessionLocal()

    try:
        category_product_count = (
            db.query(
                Category.name.label("category"),
                func.count(Product.id).label("product_count")
            )
            .join(
                Product,
                Product.category_id == Category.id
            )
            .filter(Product.is_deleted == False)
            .group_by(Category.name)
            .all()
        )

        return [
            {
                "category": category,
                "product_count": product_count
            }
            for category, product_count in category_product_count
        ]

    finally:
        db.close()

@router.get("/user-orders", dependencies=[Depends(HTTPBearer())])
def get_user_order_summary():

    db = SessionLocal()

    try:
        user_order_summary = (
            db.query(
                Order.user_id,
                func.count(Order.id).label("order_count"),
                func.sum(Order.total_amount).label("total_amount")
            )
            .group_by(Order.user_id)
            .order_by(
                func.sum(Order.total_amount).desc()
            )
            .all()
        )

        return [
            {
                "user_id": user_id,
                "order_count": order_count,
                "total_amount": total_amount
            }
            for user_id, order_count, total_amount in user_order_summary
        ]

    finally:
        db.close()

@router.get("/order-details", dependencies=[Depends(HTTPBearer())])
def get_order_details():

    db = SessionLocal()

    try:
        order_details = (
            db.query(
                Order.id,
                Order.user_id,
                Order.total_amount,
                Order.status,
                Order.created_at
            )
            .order_by(Order.created_at.desc())
            .limit(10)
            .all()
        )

        return [
            {
                "id": order_id,
                "user_id": user_id,
                "total_amount": total_amount,
                "status": status,
                "created_at": created_at
            }
            for (
                order_id,
                user_id,
                total_amount,
                status,
                created_at
            ) in order_details
        ]

    finally:
        db.close()