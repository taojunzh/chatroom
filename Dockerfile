FROM python:3.8

ENV HOME /root
WORKDIR /root

COPY . .
RUN python -m pip install Flask flask-sqlalchemy flask-socketio
RUN python -m pip install pymongo

EXPOSE 5000

CMD python3 test.py