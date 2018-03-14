/**
 * Created by lizhengqing on 2018/3/14.
 */
var redis = require('redis');
var http = require('http');
var url = require("url");
var querystring = require("querystring");
http.createServer(function (req, res) {
    // 设置接收数据编码格式为 UTF-8
    req.setEncoding('utf-8');
    var postData = ""; //POST & GET ： name=zzl&email=zzl@sina.com
    // 数据块接收中
    req.addListener("data", function (postDataChunk) {
        postData += postDataChunk;
    });
    // 数据接收完毕，执行回调函数
    req.addListener("end", function () {
        console.log('数据接收完毕');
        var params = querystring.parse(postData);//GET & POST  ////解释表单数据部分{name="zzl",email="zzl@sina.com"}
        console.log(params);
        console.log(params["name"]);
        PushToRedis(params["name"]);
        res.writeHead(500, {
            "Content-Type": "text/plain;charset=utf-8"
        });
        res.end("数据提交完毕");
    });
}).listen(8000, "127.0.0.1");
console.log('Server running at http://127.0.0.1:8000/');

//表单接收完成后，再处理redis部分
function PushToRedis(info) {
    var client = redis.createClient('6379','192.168.10.52');
    client.lpush("topnews", info);
    console.log("PushToRedis:" + info);
    client.lpop("topnews", function (i, o) {
        console.log(o);//回调，所以info可能没法得到o的值，就被res.write输出了
    })
    client.quit();
}