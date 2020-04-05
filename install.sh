#!/bin/bash
cd /app
sleep 5
git clone https://github.com/NiharZanwar/face-recog-server.git
cd face-recog-server

cd /data;
python -m http.server 8008 &
cd /app
python app.py