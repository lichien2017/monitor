#!/bin/bash
mv Dockerfile_python3_adb Dockerfile
docker build -t tymx/ecological:py3 .
