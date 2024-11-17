import os
import pika
from concurrent.futures import ThreadPoolExecutor


class RabbitClient:

    def __init__(self):
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                os.environ.get("RABBITMQ_HOST"),
                os.environ.get("RABBITMQ_PORT"),
                '/',
                pika.PlainCredentials(
                    username=os.environ.get("RABBITMQ_USERNAME"),
                    password=os.environ.get("RABBITMQ_PASSWORD"))))

        self._queue_name = os.environ.get("RABBITMQ_QUEUE_NAME")
        self._channel = self._connection.channel()

    def publish(self, data):
        self._channel.basic_publish(exchange='',
                              routing_key='anchoring',
                              body=data)

    def publish_multiple(self, data):
        MAX_THREADS = 8
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            executor.map(self.publish, data)