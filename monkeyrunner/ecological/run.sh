#!/bin/sh

pip install --no-cache-dir -r requirements.txt &&
echo "准备开始执行" &&
python main.py &&
echo "准备开始执行..."