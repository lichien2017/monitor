#!/bin/bash
echo '执行开始'
docker run --rm --net=pub_mobilephone_release -v /home/tymx/Documents/DockerContainer/ECOServer:/usr/local/ECOServer -v /mnt/train_files:/tmp pub_ecoserver python /usr/local/ECOServer/importtraindata.py
echo '结束'