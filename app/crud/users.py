from sqlalchemy.orm import Session

from app.models import Users

def user_exists_by_id(db: Session, user_id):
    user = db.query(Users).filter(Users.user_id == user_id).first()
    return [True, user] if user else [False]