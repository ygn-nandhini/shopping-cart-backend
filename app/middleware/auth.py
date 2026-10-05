from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt, JWTError

from app.settings import settings


async def auth_middleware(request: Request, call_next):

    public_paths = [
        "/docs",
        "/openapi.json",
        "/redoc",
        "/login"
    ]

    # POST /users = New user signup
    if request.method == "POST" and request.url.path == "/users":
        return await call_next(request)

    # Public paths
    if request.url.path in public_paths:
        return await call_next(request)

    authorization = request.headers.get("Authorization")

    if not authorization:
        return JSONResponse(
            status_code=401,
            content={"detail": "Authorization token required"}
        )

    try:
        scheme, token = authorization.split(" ")

        if scheme.lower() != "bearer":
            raise JWTError()

        jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

    except (JWTError, ValueError):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or expired token"}
        )

    return await call_next(request)