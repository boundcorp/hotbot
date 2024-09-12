#!/usr/bin/env bash


make frontend_deps
make generate

echo "Mountaineer dev server only runs on localhost, using socat to bind local port 7999 to expose 8000 on docker container..."
socat TCP-LISTEN:8000,fork TCP:127.0.0.1:7999 &
python3 -m hotbot.cli runserver --port 7999