FROM python:3.8-slim-buster
MAINTAINER Yaroslav Yanin 'yaninyaroslav@yandex.ru'
WORKDIR /flask_client
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
