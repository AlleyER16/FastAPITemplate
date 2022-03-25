from enum import unique
from .database.orm_db import Base
from sqlalchemy import Column, INTEGER, String, TIMESTAMP, text

class Users(Base):
    __tablename__ = "users"

    user_id = Column(INTEGER, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    age = Column(INTEGER, nullable=False)
    email_address = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))