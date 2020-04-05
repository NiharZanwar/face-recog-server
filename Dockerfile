FROM python:3


RUN apt-get update
RUN	apt-get install -y cmake
RUN	mkdir /app /data
RUN	pip install flask face_recognition pymysql configparser

COPY install.sh /app

RUN chmod +x /app/install.sh

ENTRYPOINT ["./app/install.sh &"]
