from jose import jwt, JWTError

SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"


def create_access_token(user_id: int):
    payload = {
        "user_id": user_id
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def get_user_id_from_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")

        return user_id

    except JWTError:
        return None