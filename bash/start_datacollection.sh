#!/bin/bash
docker run --rm --net=pub_mobilephone_release -v /home/tymx/Documents/DockerContainer/ECOServer:/usr/local/ECOServer -v /mnt/train_files:/tmp pub_ecoserver python /usr/local/ECOServer/data_collection_main.py