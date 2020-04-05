FROM python:3


RUN apt-get update
RUN	apt-get install -y cmake
RUN	mkdir /app /data
RUN	pip install flask face_recognition pymysql configparser

COPY install.sh /app

EXPOSE 5005/tcp
EXPOSE 8008/tcp