import streamlit as st
from sqlalchemy import func

from app.database import SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.category import Category


# Page Configuration
st.set_page_config(
    page_title="Shopping Cart Dashboard",
    page_icon="🛒",
    layout="wide"
)


st.title("🛒 Shopping Cart Dashboard")
st.write("Overview of users, products, orders and sales")


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

    recent_orders = (
        db.query(Order)
        .order_by(Order.created_at.desc())
        .limit(5)
        .all()
    )

    products = (
        db.query(Product)
        .filter(Product.is_deleted == False)
        .order_by(Product.stock.asc())
        .limit(5)
        .all()
    )

    order_status = (
        db.query(
            func.upper(Order.status),
            func.count(Order.id)
        )
        .group_by(func.upper(Order.status))
        .all()
    )

    category_product_count = (
        db.query(
            Category.name,
            func.count(Product.id)
        )
        .join(
            Product,
            Product.category_id == Category.id
        )
        .filter(Product.is_deleted == False)
        .group_by(Category.name)
        .all()
    )

    user_order_summary = (
        db.query(
            Order.user_id,
            func.count(Order.id),
            func.sum(Order.total_amount)
        )
        .group_by(Order.user_id)
        .order_by(func.sum(Order.total_amount).desc())
        .all()
    )

#order detalis 
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

finally:
    db.close()


# =====================================================
# Dashboard Metrics
# =====================================================

st.subheader("Dashboard Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Users",
    total_users
)

col2.metric(
    "Total Products",
    total_products
)

col3.metric(
    "Total Orders",
    total_orders
)

col4.metric(
    "Total Order Amount",
    f"₹{total_order_amount:,.2f}"
)


st.divider()


# =====================================================
# Recent Orders
# =====================================================

st.subheader("Recent Orders")

if recent_orders:

    for order in recent_orders:

        st.write(
            f"Order ID: {order.id} | "
            f"User ID: {order.user_id} | "
            f"Amount: ₹{order.total_amount:.2f} | "
            f"Status: {order.status}"
        )

else:

    st.write("No orders found.")


st.divider()


# =====================================================
# Product Stock
# =====================================================

st.subheader("Product Stock")

if products:

    for product in products:

        st.write(
            f"Product: {product.name} | "
            f"Stock: {product.stock}"
        )

else:

    st.write("No products found.")


st.divider()


# =====================================================
# Order Status Summary
# =====================================================

st.subheader("Order Status Summary")

if order_status:

    for status, count in order_status:

        st.write(
            f"{status}: {count}"
        )

else:

    st.write("No order status data found.")


st.divider()


# =====================================================
# Category-wise Product Count
# =====================================================

st.subheader("Category-wise Product Count")

if category_product_count:

    for category, count in category_product_count:

        st.write(
            f"Category: {category} | "
            f"Products: {count}"
        )

else:

    st.write("No category data found.")


st.divider()


# =====================================================
# User-wise Order Summary
# =====================================================

st.subheader("User-wise Order Summary")

if user_order_summary:

    for user_id, order_count, order_amount in user_order_summary:

        st.write(
            f"User ID: {user_id} | "
            f"Orders: {order_count} | "
            f"Total Amount: ₹{order_amount:,.2f}"
        )

else:

    st.write("No user order data found.")


st.divider()


# =====================================================
# Order Details Table
# =====================================================

st.subheader("Order Details")

if order_details:

    order_table = []

    for order in order_details:

        order_table.append({
            "Order ID": order.id,
            "User ID": order.user_id,
            "Total Amount": f"₹{order.total_amount:,.2f}",
            "Status": order.status.upper(),
            "Created At": order.created_at.strftime(
                "%d-%m-%Y %I:%M %p"
            )
        })

    st.table(order_table)

else:

    st.write("No order details found.")


st.divider()


# =====================================================
# Footer
# =====================================================

st.caption(
    "Shopping Cart Dashboard | Data fetched from PostgreSQL"
)



