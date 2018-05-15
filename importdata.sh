#!/bin/bash
echo '执行开始'
docker run --rm --net=dockercontainer_mobilephone -v /home/tymx/Documents/DockerContainer/ECOServer:/usr/local/ECOServer -v /mnt/train_files:/tmp tymx/ecoserver:v2 python /usr/local/ECOServer/importtraindata.py
echo '结束'