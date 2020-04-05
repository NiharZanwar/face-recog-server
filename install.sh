#!/bin/bash
cd /app
sleep 5
git clone https://github.com/NiharZanwar/face-recog-server.git
cd face-recog-server
echo "clone complete"
cd /app/face-recog-server
python app.py
cd /data;
python -m http.server 8008 &
echo "http server runnong"

