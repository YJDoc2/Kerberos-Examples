#! /bin/bash

MYROOT=$PWD

cd "$MYROOT/KDC" && python3 app.py & 
cd "$MYROOT/data-server" && python3 A.py &
cd "$MYROOT/data-server" && python3 B.py 
