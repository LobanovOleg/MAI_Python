from sqlalchemy.orm import Session
from models import User, LoginHistory
from auth import get_password_hash
from schemas import UserCreate

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def add_login_history(db: Session, user_id: int):
    login_history = LoginHistory(user_id=user_id)
    db.add(login_history)
    db.commit()
    db.refresh(login_history)
    return login_history