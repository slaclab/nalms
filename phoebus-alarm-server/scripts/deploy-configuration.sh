#!/usr/bin/env bash
docker run -v $2:/tmp/nalms/$1.xml -it phoebus-alarm-server start-server $1 /tmp/nalms/$1.xml