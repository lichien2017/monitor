var express = require('express');
var redis = require('redis');

var router = express.Router();

var redisIp = 'redisdb';

/* GET home page. */
router.get('/', function(req, res, next) {
  // res.render('index', { title: 'Express' });
    try{
        var client  = redis.createClient('6379', redisIp);

        client.on('connect', function() {
            console.log('connected');

            // var ruler = [];
            // var rulerItem = {};
            // rulerItem.regStr =  encodeURIComponent('.+?\.snssdk\.com\/api\/news\/feed\/v');
            // rulerItem.tag = 'snssdk';
            // ruler.push(rulerItem);
            //
            // client.set('ruler',JSON.stringify(ruler));
            //先把数据存进去
            client.get('ruler',function (err,rulerString) {
                // var obj  = JSON.parse(rulerString);
                // var regex1 = RegExp(decodeURIComponent(obj[0].regStr),'i');

                // console.log(regex1.test("if.snssdk.com/api/news/feed/v78"));
                res.send({"status": "success","data":rulerString});
            });//得到规则字符串

        });

        // redis 链接错误
        client.on("error", function(error) {
            console.log(error);
        });

    }catch (e){
        res.send({"status": "error"});
        console.log(e);
    }
});


/**
 * 获取规则文件
 */
router.get('/ruler', function (req, res) {
    try{
        var client  = redis.createClient('6379', redisIp);

        client.on('connect', function() {
            console.log('connected');
            //先把数据存进去
            var rulerString =  client.get('ruler',redis.print);//得到规则字符串
            res.send({"status": "success","data":rulerString});
        });

        // redis 链接错误
        client.on("error", function(error) {
            console.log(error);
        });

    }catch (e){
        res.send({"status": "error"});
        console.log(e);
    }
    //res.send({"status": "success"});
});

/**
 * 处理发过来的数据包
 */
router.post('/pkg', function (req, res) {
    console.log(req.body);
    try{
        parseJsonDataAndSendToRedis(req.body);
    }catch (e){
        console.log(e);
    }
    res.send({"status": "success"});
});
/**
 * 解析数据并写入到redis
 * @param jsonObj 待发送的数据
 */
function parseJsonDataAndSendToRedis(jsonObj) {

    var tag = decodeURIComponent(jsonObj.tag);//消息队列标示
    var url = decodeURIComponent(jsonObj.url);//数据请求的地址，这里可以用区分是哪个频道
    var data = decodeURIComponent(jsonObj.str);//真实的数据
    var post = decodeURIComponent(jsonObj.post);//postData数据
    var time = jsonObj.time;//包的时间戳

    console.log(tag);
    console.log(url);
    console.log(data);
    console.log(time);

    var storeData = {};//构造新的数据结构
    storeData.url = url;
    storeData.data = data;
    storeData.time = time;
    storeData.post = post;

    var storeString = JSON.stringify(storeData);

    var client  = redis.createClient('6379', redisIp);

    client.on('connect', function() {
        console.log('connected');
        //先把数据存进去
        client.lpush('origin:'+tag,storeString,function (err,obj) {
            console.log(obj);
            client.end(true);
        });


    });

    // redis 链接错误
    client.on("error", function(error) {
        console.log(error);
    });

}
module.exports = router;
