FROM golang

WORKDIR $GOPATH/src/github.com/imgserver
COPY . $GOPATH/src/github.com/imgserver
RUN go build .

EXPOSE 9001
ENTRYPOINT ["./imgserver"]
