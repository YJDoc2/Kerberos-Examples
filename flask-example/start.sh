#! /bin/bash

MYROOT=$PWD

cd "$MYROOT/KDC" && pipenv run python3 app.py & 
cd "$MYROOT/data-server" && pipenv run python3 A.py &
cd "$MYROOT/data-server" && pipenv run python3 B.py 
