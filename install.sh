#!/bin/bash
cd /app;
git clone https://github.com/NiharZanwar/docker_testing.git;
cd docker_testing;
python app.py &
python -m http.server 8008 &