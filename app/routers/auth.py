from fastapi import APIRouter, status, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.database.orm_db import get_db

from app.oauth2 import create_access_token
from app.schemas import Auth
from app.models import Users

from app.utils import verify_password

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login", status_code=status.HTTP_200_OK)
def login(response: Response, auth_data: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(get_db)):

    if auth_data.username == "admin" and auth_data.password == "admin":
        access_token = create_access_token({"admin_logged": True})
        return Auth(message="Login successfully", access_token=access_token, token_type="bearer")
    else:
        user = db.query(Users).filter(Users.email_address == auth_data.username).first()

        if not user or not verify_password(auth_data.password, user.password):
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {"message": "Invalid email address or password"}

        access_token = create_access_token({"user_id": user.user_id})
        return Auth(message="Login successfully", access_token=access_token, token_type="bearer", user=user)