var express = require('express');
var redis = require('redis');
var mongodb = require('mongodb');
var formidable = require('formidable');
const path = require('path');
const fs = require('fs');


// var MongoClient = require('mongodb').MongoClient
//     , Server = require('mongodb').Server;


var router = express.Router();

var debug = true;
var redisIp ='192.168.10.176';//container里面的redisdb名称
var redisPort = 6379
var mongodbIp = '192.168.10.176';//container里面的mongodb名称
var mongodbPort = 27017
var uploadpath = '/usr/local/nodejsqueue/redisService/uploads/';//图片保存路径

if (debug){
    redisIp = '192.168.10.176';
    mongodbIp= '192.168.10.176';
    uploadpath =path.join(process.cwd() + "/../uploads");
}

var DB_CONN_STR = 'mongodb://'+mongodbIp+':'+mongodbPort+'/crawlnews';
/**
 * 测试地址
 */
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
            // client.set('rules',JSON.stringify(ruler));
            //先把数据存进去
            client.get('rules',function (err,rulerString) {
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



router.get('/applist',function (req,res) {
    try{
        var client  = redis.createClient('6379', redisIp);

        client.on('connect', function() {
            console.log('connected');
            //先把数据存进去
            // var dataList = [];
            // var data = {};
            // data.tag = 'snssdk';
            // data.pkg = 'com.ss.android.article.news';
            // dataList.push(data);
            // client.set('applist',JSON.stringify(dataList),redis.print);
            // var rulerString =  client.get('applist',redis.print);//得到规则字符串
            client.get('applist',function (err,result) {
                //得到规则字符串
                res.json({"status": "success","data":result});
            });
        });

        // redis 链接错误
        client.on("error", function(error) {
            console.log(error);
        });

    }catch (e){
        res.json({"status": "error"});
        console.log(e);
    }
});

/**
 * 接收上传图片
 */
router.post("/image",function (req,res) {
    console.log("开始接收上传文件");
    try{
        var form = new formidable.IncomingForm();
        form.encoding = 'utf-8';
        form.uploadDir = uploadpath;//path.join(process.cwd() + "/../uploads");
        console.log(form.uploadDir);
        form.keepExtensions = true;//保留后缀
        form.maxFieldsSize = 20 * 1024 * 1024;
        //处理图片
        form.parse(req, function (err, fields, files){
            var filename = files.uploadfile.name
            console.log('filename='+filename);
            // var nameArray = filename.split('.');
            // var type = nameArray[nameArray.length - 1];
            // var name = '';
            // for (var i = 0; i < nameArray.length - 1; i++) {
            //     name = name + nameArray[i];
            // }
            // var date = new Date();
            //var time = '_' + date.getFullYear() + "_" + date.getMonth() + "_" + date.getDay() + "_" + date.getHours() + "_" + date.getMinutes();
            // var avatarName = name  + '.' + type;
            var newPath = form.uploadDir + "/" + filename;
            console.log('newPath='+newPath);
            fs.renameSync(files.uploadfile.path, newPath);  //重命名
            res.send({"status": "success"});
        })
    }catch (e){
        console.log(e)
        res.send({"status": "error"});
    }

});



/**
 * 插入原始push消息数据
 * @param db mongodb数据库
 * @param callback 回调
 */
var insertPushData = function(db, insertData,callback) {
    //连接到表
    var collection = db.collection('push');
    //插入数据
    collection.insertOne(insertData,function (err,result) {
        if(err)
        {
            console.log('Error:'+ err);
            return;
        }
        callback(result);
    });
}
/**
 * 接收push通知
 */
router.post("/push",function (req,res) {
    console.log("收到push消息："+req.body);
    try{

        // var mongoClient = new MongoClient(new Server(mongodbIp, 27017));
        // mongoClient.open(function(err, mongoClient) {
        //     if(err){
        //         console.log(err);
        //         return;
        //     }
        //     console.log("mongodb连接成功！");
        //     var db1 = mongoClient.db("crawlnews");
        //
        //     insertPushData(db1, req.body,function(result) {
        //         console.log(result);
        //         mongoClient.close();
        //         res.json({"status": "success"});
        //     });
        //
        // });

        var MongoClient = mongodb.MongoClient;
        MongoClient.connect(DB_CONN_STR, function(err, db) {
            console.log("mongodb连接成功！");
            //将接收到的数据插入数据库
            insertPushData(db.db('crawlnews'), req.body,function(result) {
                console.log(result);
                db.close();
                res.json({"status": "success"});
            });
        });

    }catch (e){
        console.log(e);
        res.json({"status": "error"});

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
            client.get('ruler',function (err,result) {
                //得到规则字符串
                res.send({"status": "success","data":result});
            });

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
 * 获取图片
 */
router.get('/filename', function (req, res) {
    try{
        var filePath = path.join(uploadpath, req.query.fn);
        fs.exists(filePath, function (exists) {
            res.sendfile(exists ? filePath : path.join(uploadpath, ""));
        });

    }catch (e){
        res.send({"status": "error"});
        console.log(e);
    }
    //res.send({"status": "success"});
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

    var client  = redis.createClient(redisPort, redisIp);

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
