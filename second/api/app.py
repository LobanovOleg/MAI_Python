from fastapi import FastAPI, HTTPException
from typing import  Optional
from pydantic import BaseModel
import pika
from auth.models import Session, User, LoginHistory
from auth.providers.yandex import YandexAuth
from auth.providers.vk import VKAuth
import logging
from auth.utils import hash_password, check_password
from dotenv import load_dotenv
import os

load_dotenv()

# Конфигурация RabbitMQ
RABBITMQ_HOST_ENV = os.getenv("RABBITMQ_HOST")
RABBITMQ_QUEUE_ENV = os.getenv("RABBITMQ_QUEUE")

# Конфигурация Yandex и VK
YANDEX_CLIENT_ID_ENV = os.getenv("YANDEX_CLIENT_ID")
YANDEX_CLIENT_SECRET_ENV = os.getenv("YANDEX_CLIENT_SECRET")
YANDEX_REDIRECT_URI_ENV = os.getenv("YANDEX_REDIRECT_URI")

VK_CLIENT_ID_ENV = os.getenv("VK_CLIENT_ID")
VK_CLIENT_SECRET_ENV = os.getenv("VK_CLIENT_SECRET")
VK_REDIRECT_URI_ENV = os.getenv("VK_REDIRECT_URI")

TG_TOKEN_ENV = os.getenv("TG_TOKEN")

app = FastAPI()

yandex_auth = YandexAuth(YANDEX_CLIENT_ID_ENV, YANDEX_CLIENT_SECRET_ENV, YANDEX_REDIRECT_URI_ENV)
vk_auth = VKAuth(VK_CLIENT_ID_ENV, VK_CLIENT_SECRET_ENV, VK_REDIRECT_URI_ENV)

class AuthRequest(BaseModel):
    code: str

class EmailAuthRequest(BaseModel):
    email: str
    password: str
    telegram_id: Optional[str] = None
    allow_notifications: bool = True


def send_to_rabbitmq(message: str):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST_ENV,
                credentials=pika.PlainCredentials('myuser', 'mypassword')
            )
        )
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE_ENV, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE_ENV,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        logging.error(f"Ошибка: {e}")

@app.post("/register")
async def register(request: EmailAuthRequest):
    email = request.email
    password = request.password
    telegram_id = request.telegram_id
    allow_notifications = request.allow_notifications

    session = Session()
    user = session.query(User).filter_by(email=email).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(password)
    new_user = User(
        email=email,
        password=hashed_password,
        telegram_id=telegram_id,
        allow_notifications=allow_notifications
    )

    new_user = User(email=email, password=hashed_password)
    session.add(new_user)
    session.commit()

    if allow_notifications and telegram_id:
        send_to_rabbitmq(f"{telegram_id}|Успешная регистрация|{TG_TOKEN_ENV}")
    if request.allow_notifications and not request.telegram_id:
        raise HTTPException(status_code=400, detail="Telegram ID required for notifications")
    return {"message": "User registered successfully"}

# Регистрация через Yandex
@app.post("/auth/yandex")
async def auth_yandex(request: AuthRequest):
    code = request.code
    token = yandex_auth.get_token(code)
    user_info = yandex_auth.get_user_info(token)

    session = Session()
    user = session.query(User).filter_by(email=user_info["email"]).first()
    if not user:
        user = User(email=user_info["email"])
        session.add(user)
        session.commit()
        send_to_rabbitmq(f"{user_info['email']}|Добро пожаловать!|{TG_TOKEN_ENV}")

    login_history = LoginHistory(user_id=user.id, provider="yandex")
    session.add(login_history)
    session.commit()
    return {"message": "Authenticated via Yandex"}

# Регистрация через VK
@app.post("/auth/vk")
async def auth_vk(request: AuthRequest):
    code = request.code
    token = vk_auth.get_token(code)
    user_info = vk_auth.get_user_info(token)

    session = Session()
    user = session.query(User).filter_by(email=user_info["email"]).first()
    if not user:
        user = User(email=user_info["email"])
        session.add(user)
        session.commit()
        send_to_rabbitmq(f"{user_info['email']}|Добро пожаловать!|{TG_TOKEN_ENV}")

    login_history = LoginHistory(user_id=user.id, provider="vk")
    session.add(login_history)
    session.commit()
    return {"message": "Authenticated via VK"}
    
@app.post("/auth/email")
async def auth_email(request: EmailAuthRequest):
    email = request.email
    password = request.password

    session = Session()
    user = session.query(User).filter_by(email=email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not user.password:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not check_password(user.password, password):
        raise HTTPException(status_code=400, detail="Invalid email or password")