from app.database import SessionLocal
from app.models.user import User
from app.auth.password import hash_password


db = SessionLocal()

try:
    users = db.query(User).all()

    for user in users:
        user.hashed_password = hash_password(user.hashed_password)

    db.commit()

    print("All existing passwords have been hashed successfully.")

finally:
    db.close()