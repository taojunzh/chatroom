FROM python:3.8

ENV HOME /root
WORKDIR /root

COPY . .

RUN python -m pip install Flask flask-socketio flask_login flask-pymongo


RUN python -m pip install pymongo requests bcrypt

EXPOSE 5000

CMD python3 test_mongo.py
