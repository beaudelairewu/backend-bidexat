FROM python:3.8.3
WORKDIR /worker

ENV APP_HOME /worker
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "${PYTHONPATH}/worker"

RUN apt-get update -y
RUN apt install libgl1-mesa-glx -y
RUN apt-get install 'ffmpeg'\
    'libsm6'\
    'libxext6'  -y
RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

CMD ["python3", "bidex-worker.py"]
