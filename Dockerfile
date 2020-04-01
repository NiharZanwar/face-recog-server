FROM python:3

RUN apt-get update
RUN	apt-get install -y cmake
RUN	mkdir app && cd app
RUN	pip install flask face_recognition pymysql configparser


EXPOSE 5005/tcp
EXPOSE 8008/tcp