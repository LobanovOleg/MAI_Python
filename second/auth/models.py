from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String, nullable=True)
    telegram_id = Column(String, nullable=True)
    allow_notifications = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

class LoginHistory(Base):
    __tablename__ = 'login_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    provider = Column(String)
    login_time = Column(DateTime, default=datetime.utcnow)

engine = create_engine('sqlite:///auth.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

if __name__ == "__main__":
    Base.metadata.create_all(engine)