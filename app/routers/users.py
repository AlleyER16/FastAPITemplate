from fastapi import APIRouter, status, Depends, Response
from app.models import Users
from app.oauth2 import get_current_user
from app.schemas import FetchMetaData, GetUser, GetUsers, AddUser

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database.orm_db import get_db
from app.database.sql_db import db, cursor
from app.utils import get_pagination, get_password_hash, get_skip

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/", status_code=status.HTTP_200_OK, response_model=GetUsers)
def get_users(response: Response, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), 
search: str = "", page: int = 1, division: int = 10):

    if current_user["user_type"] != "admin":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}

    users = db.query(Users)

    if search:
        users = users.filter(or_(func.lower(Users.first_name).contains(search.lower()), func.lower(Users.last_name).contains(search.lower()), 
        func.concat(func.lower(Users.first_name), func.lower(Users.last_name)).contains(search.lower())
        ))

    num_records = len(users.all())
    pagination = get_pagination(num_records, division)

    fetch_meta_data = FetchMetaData(num_records=num_records, pagination=pagination, page=page, division=division)

    skip = get_skip(page, division)

    users = users.offset(skip).limit(division).all()

    return {"message": "Users fetched successfully", "meta_data": fetch_meta_data, "users": users}

@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=GetUser)
def get_user(user_id: int, response: Response, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):

    user_query = db.query(Users).filter(Users.user_id == user_id)

    user = user_query.first()

    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Error identifying user"}

    if current_user["user_type"] == "admin":
        pass
    elif current_user["user_type"] == "user":
        if user_id != current_user["user"].user_id:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {"message": "Unauthorized"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}

    return {"message": "User fetched successfully", "user": user}

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GetUser)
def add_user(user: AddUser, response: Response, db: Session = Depends(get_db)):

    user_exists_by_email = db.query(func.count(Users.user_id)).filter(Users.email_address == user.email_address).scalar()

    if user_exists_by_email:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Email has been used"}

    user.password = get_password_hash(user.password)

    user = Users(**user.dict())

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User added successfully", "user": user}

@router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=GetUser)
def update_user_info(user_id: int, user_update: AddUser, response: Response, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):

    user_query = db.query(Users).filter(Users.user_id == user_id)

    user = user_query.first()

    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Error identifying user"}

    if current_user["user_type"] == "admin":
        pass
    elif current_user["user_type"] == "user":
        if user_id != current_user["user"].user_id:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {"message": "Unauthorized"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}

    if user_update.email_address != user.email_address:
        email_exists = db.query(func.count(Users.user_id)).filter(Users.email_address == user_update.email_address).scalar()
        if email_exists:
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            return {"message": "Email has been used"}

    user_update.password = get_password_hash(user_update.password)

    user_query.update(user_update.dict(), synchronize_session=False)
    db.commit()

    return {"message": "User updated successfully", "user": user_query.first()}

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int, response: Response, current_user: dict = Depends(get_current_user)):

    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Error identifying user"}

    if current_user["user_type"] == "admin":
        pass
    elif current_user["user_type"] == "user":
        if user_id != current_user["user"].user_id:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {"message": "Unauthorized"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}

    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    db.commit()

    return {"message": "User deleted successfully"}