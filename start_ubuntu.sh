#!/bin/bash -e
cd "$(dirname "$0")"
git reset --hard
git pull
echo ------ Starting Backend
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