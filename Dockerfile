FROM python:3.8

ENV HOME /root
WORKDIR /root

COPY . .
RUN python -m pip install Flask flask-sqlalchemy flask-socketio flask_login
RUN python -m pip install pymongo requests

EXPOSE 5000

CMD python3 test_mongo.py
