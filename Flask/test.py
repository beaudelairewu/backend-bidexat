import logging
import os

from flask import Flask
import redis

from rq import Queue, Connection
from rq.job import Job

app = Flask(__name__)

redis_host = os.environ.get('REDISHOST', 'localhost')
redis_port = int(os.environ.get('REDISPORT', 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port)
q = Queue(connection=redis_client)

@app.route('/')
def index():
    with Connection(redis_client):
                # job = q.enqueue_call(
                #             func='ai.ai_helper.rundetect',
                #             args=(pid, folderID, imgsize),
                #             result_ttl=5000
                #             )pid=pid, cluster=cluster, subCluster=subCluster, size=imgsize
                job = q.enqueue('asdf.helloworld')
                jobid = job.get_id()
    return jobid


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))