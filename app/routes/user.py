from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.auth.password import hash_password
from app.auth.jwt import get_user_id_from_token
from app.services.audit_service import create_audit_log

router = APIRouter()
security = HTTPBearer()


@router.post(
    "/users",
    response_model=UserOut
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    create_audit_log(
        db=db,
        user_id=new_user.id,
        action="CREATE",
        table_name="users",
        record_id=new_user.id,
        old_values=None,
        new_values={"name": new_user.name, "email": new_user.email}
    )
    db.commit()

    return new_user


@router.get(
    "/users",
    response_model=list[UserOut],
    dependencies=[Depends(security)]
)
def get_users(
    db: Session = Depends(get_db)
):
    users = db.query(User).filter(
        User.is_deleted == False
    ).all()
    return users


@router.put(
    "/users/{user_id}",
    response_model=UserOut,
    dependencies=[Depends(security)]
)
def update_user(
    user_id: int,
    user: UserCreate,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    existing_user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()

    if not existing_user:
        return {"detail": "User not found"}

    old_values = {"name": existing_user.name, "email": existing_user.email}

    existing_user.name = user.name
    existing_user.email = user.email
    existing_user.hashed_password = hash_password(user.password)

    new_values = {"name": user.name, "email": user.email}

    db.commit()
    db.refresh(existing_user)

    current_user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=current_user_id,
        action="UPDATE",
        table_name="users",
        record_id=user_id,
        old_values=old_values,
        new_values=new_values
    )
    db.commit()

    return existing_user


@router.delete(
    "/users/{user_id}",
    dependencies=[Depends(security)]
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    existing_user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()

    if not existing_user:
        return {"detail": "User not found"}

    old_values = {"is_deleted": existing_user.is_deleted}

    existing_user.is_deleted = True

    new_values = {"is_deleted": True}

    db.commit()
    db.refresh(existing_user)

    current_user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=current_user_id,
        action="DELETE",
        table_name="users",
        record_id=user_id,
        old_values=old_values,
        new_values=new_values
    )
    db.commit()

    return {"message": "User deleted successfully"}