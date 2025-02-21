import pika
import requests
from dotenv import load_dotenv
import os

load_dotenv()

def send_telegram_message(chat_id, message, token):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
    }
    requests.post(url, json=payload)

def start_worker():
    credentials = pika.PlainCredentials('myuser', 'mypassword')
    parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)

    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(
            queue='telegram_messages',
            durable=True
        )

        channel.basic_consume(
            queue='telegram_messages',
            on_message_callback=callback,
            auto_ack=True
        )

        print(" [*] Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Failed to connect to RabbitMQ: {e}")

def callback(ch, method, properties, body):
    try:
        data = body.decode().split('|')
        chat_id, message, token = data
        print(f"Sending to chat_id: {chat_id}, message: {message}")
        send_telegram_message(chat_id, message, token)
    except Exception as e:
        print(f"Error processing message: {e}")

if __name__ == "__main__":
    start_worker()