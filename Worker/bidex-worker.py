import redis
from rq import Worker, Queue, Connection
import os

listen = ['default']
redis_client = redis.from_url('redis://redis:6379')

if __name__ == '__main__':
    with Connection(redis_client):
        worker = Worker(list(map(Queue, listen)))
        worker.work()