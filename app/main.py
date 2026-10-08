from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.auth import auth_middleware
from app.settings import settings
from app.routes import (
    category,
    product,
    cart,
    user,
    cart_item,
    order,
    order_item,
    login,
    audit_log,
    dashboard
)


app = FastAPI(debug=True)
# Auth middleware
app.middleware("http")(auth_middleware)
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Shopping Cart Backend API is running  - Feature Branch"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(category.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(user.router)
app.include_router(cart_item.router)
app.include_router(order.router)
app.include_router(order_item.router)
app.include_router(login.router)
app.include_router(audit_log.router)
app.include_router(dashboard.router)
