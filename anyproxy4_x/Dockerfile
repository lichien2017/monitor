FROM node:6.9.2
MAINTAINER lichien@qq.com
EXPOSE 8001
EXPOSE 8002
EXPOSE 8103

RUN mkdir /usr/local/anyproxy


RUN npm install -g anyproxy
RUN anyproxy-ca -g

ENTRYPOINT ["anyproxy"]
