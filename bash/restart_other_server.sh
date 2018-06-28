#!/bin/bash
docker-compose -f ../pub/docker-compose.yml restart mitmproxy
docker-compose -f ../pub/docker-compose.yml restart ecoserver