#! /bin/bash
MYROOT=$PWD

cd "$MYROOT/client" && python3 client.py &
cd "$MYROOT/Servers" && npm run start 