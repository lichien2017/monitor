#!/bin/bash
mv Dockerfile_python2 Dockerfile
docker build -t tymx/ecological:v1 .
