import logging
import os

from flask import Flask, request
import redis

from rq import Queue, Connection
from rq.job import Job

from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

# redis_host = os.environ.get('REDISHOST', 'localhost')
# redis_port = int(os.environ.get('REDISPORT', 6379))
# redis_client = redis.Redis(host=redis_host, port=redis_port)
redis_client = redis.from_url('redis://redis:6379')
q = Queue(connection=redis_client)

@app.route('/')
def index():
    return 'helloworld'

@app.route('/detectov', methods=["POST"])
def detectov():
    if request.method == "POST":
        userID = request.form['userID']
        patientID = request.form['patientID']
        slideID = request.form['slideID']
        image_name_list = request.form['image_name_list']
        image_name_list = image_name_list.split(',')
        with Connection(redis_client):
            job = q.enqueue('fb_helper.fullcycle', userID=userID, patientID=patientID, slideID=slideID, image_name_list=image_name_list)
            jobid = job.get_id()

        return jobid

@app.route('/testing', methods=["POST"])
def testing():
    if request.method == "POST":
        image_name_list = request.form.getlist('image_name_list')
        print(type(image_name_list))
        print(image_name_list)

        return "ye"

@app.route("/result/<job_id>")
def get_result(job_id):
    job = Job.fetch(job_id, connection=redis_client)
    if job.is_finished:
        return str(job.result), 200
    else:
        return "Job not finished", 202

@app.route('/visitor')
def visitor():
    value = redis_client.incr('counter', 1)
    return 'Visitor number: {}'.format(value)

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))