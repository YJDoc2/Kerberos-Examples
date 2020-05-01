#! /bin/bash
MYROOT=$PWD

cd "$MYROOT/client" && pipenv run python3 client.py &
cd "$MYROOT/Servers" && npm run start 