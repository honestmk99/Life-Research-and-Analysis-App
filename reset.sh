#!/bin/bash -e
cd "$(dirname "$0")"
docker compose down
docker compose rm --force -v  # removes image and volumes
echo ---- Delete ./react/node_modules
rm -r ./react/node_modules