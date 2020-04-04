#!/bin/bash
cd /app;
git clone https://github.com/NiharZanwar/face-recog-server.git;
cd face-recog-server;
python app.py &
cd /data;
python -m http.server 8008 &