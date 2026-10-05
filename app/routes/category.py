from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryOut
from app.auth.jwt import get_user_id_from_token
from app.services.audit_service import create_audit_log

router = APIRouter()

security = HTTPBearer()


@router.post(
    "/categories",
    response_model=CategoryOut,
    dependencies=[Depends(security)]
)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    new_category = Category(
        name=category.name
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="CREATE",
        table_name="categories",
        record_id=new_category.id,
        old_values=None,
        new_values={"name": new_category.name}
    )
    db.commit()

    return new_category


@router.get(
    "/categories",
    response_model=list[CategoryOut],
    dependencies=[Depends(security)]
)
def get_categories(
    db: Session = Depends(get_db)
):
    categories = db.query(Category).filter(
        Category.is_deleted == False
    ).all()

    return categories


@router.put(
    "/categories/{category_id}",
    response_model=CategoryOut,
    dependencies=[Depends(security)]
)
def update_category(
    category_id: int,
    category: CategoryCreate,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    existing_category = db.query(Category).filter(
        Category.id == category_id,
        Category.is_deleted == False
    ).first()

    if not existing_category:
        return {"detail": "Category not found"}

    old_values = {"name": existing_category.name}

    existing_category.name = category.name

    new_values = {"name": category.name}

    db.commit()
    db.refresh(existing_category)

    user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        table_name="categories",
        record_id=category_id,
        old_values=old_values,
        new_values=new_values
    )
    db.commit()

    return existing_category


@router.delete(
    "/categories/{category_id}",
    dependencies=[Depends(security)]
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    token=Depends(security)
):
    existing_category = db.query(Category).filter(
        Category.id == category_id,
        Category.is_deleted == False
    ).first()

    if not existing_category:
        return {"detail": "Category not found"}

    old_values = {"is_deleted": existing_category.is_deleted}

    existing_category.is_deleted = True

    new_values = {"is_deleted": True}

    db.commit()
    db.refresh(existing_category)

    user_id = get_user_id_from_token(token.credentials)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="DELETE",
        table_name="categories",
        record_id=category_id,
        old_values=old_values,
        new_values=new_values
    )
    db.commit()

    return {"message": "Category deleted successfully"}