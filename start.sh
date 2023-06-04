#!/bin/bash -e
cd "$(dirname "$0")"
echo ------ Starting Backend
git pull
docker-compose build
echo ------ Docker Build Complete
docker-compose up -d
echo ------ Started Backend
cd react
echo ------ Starting Frontend
npm install
npm start

cmd /k
# PAUSE