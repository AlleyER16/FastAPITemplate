from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.database.orm_db import get_db

from sqlalchemy.orm import Session

from app.settings import settings

from app.crud.users import user_exists_by_id

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRATION_IN_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token

def verify_access_token(token: str, credential_exception) -> dict:
    
    try:

        token_decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except JWTError as err:
        print(err)
        raise credential_exception

    return token_decoded

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    decoded_token = verify_access_token(token, credentials_exception)

    if "admin_logged" in decoded_token.keys():
        return {"user_type": "admin"}
    elif "user_id" in decoded_token.keys():
        user_exists = user_exists_by_id(db, decoded_token["user_id"])
        if not user_exists[0]:
            raise credentials_exception
        else:
            return {"user_type": "user", "user": user_exists[1]}
    else:
        raise credentials_exception