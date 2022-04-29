import redis
from rq import Worker, Queue, Connection
import os

listen = ['default']

redis_host = os.environ.get('REDISHOST', 'localhost')
redis_port = int(os.environ.get('REDISPORT', 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port)

if __name__ == '__main__':
    with Connection(redis_client):
        worker = Worker(list(map(Queue, listen)))
        worker.work()