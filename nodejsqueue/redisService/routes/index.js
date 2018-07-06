var express = require('express');
var redis = require('redis');
var mongodb = require('mongodb');
var formidable = require('formidable');
const path = require('path');
const fs = require('fs');


// var MongoClient = require('mongodb').MongoClient
//     , Server = require('mongodb').Server;


var router = express.Router();

var debug = false;
var redisIp ="redisdb";//container里面的redisdb名称
var redisPort = 6379
var mongodbIp = "mongodb";//container里面的mongodb名称
var mongodbPort = 27017
var uploadpath = '/usr/local/nodejsqueue/redisService/uploads/';//图片保存路径
if (debug){
    redisIp = '192.168.10.177';
    mongodbIp= '192.168.10.177';
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
            var paths = filename.split("_");
            console.log(paths)
            mkdirsSync(form.uploadDir + path.sep + paths[0]);
            var newPath = form.uploadDir + path.sep + paths[0]+path.sep+ paths[1];
            console.log('newPath='+newPath);
            fs.renameSync(files.uploadfile.path, newPath);  //重命名
            res.send({"status": "success"});
        })
    }catch (e){
        console.log(e)
        res.send({"status": "error"});
    }

});

//创建多层文件夹 同步
function mkdirsSync(dirpath, mode) {
    if (!fs.existsSync(dirpath)) {
        fs.mkdirSync(dirpath, mode);

    }
    return true;
}

var sendToMediaQueue=function (data) {
    try{
        var client  = redis.createClient('6379', redisIp);
        client.on('connect', function() {
            console.log('connected');
            client.lpush('media:download',JSON.stringify(data))
        });
        // redis 链接错误
        client.on("error", function(error) {
            console.log(error);
        });

    }catch (e){
        console.log(e);
    }
}
/**
 * 生成guid
 * @returns {string}
 */
function guid() {
    function S4() {
        return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
    }
    return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}

/**
 * 将数据插入原始数据表
 * @param db
 * @param insertData
 * @param callback
 */
var insertPushDataToOriginDb = function (db,insertData,callback) {
    var day = insertData.time.substr(0,10);
    day = day.replace("-","");
    day = day.replace("-","");
    var tablename = "originnews" + day;

    console.log("insertPushDataToOriginDb！"+tablename);
    var timestamp = Date.parse(new Date(insertData.time));


    //统一时间格式
    insertData.imgfilename =insertData.imgfilename.replace("_","/")
    //console.log('insertData:'+ insertData.imgfilename);

    var originNews = {};
    originNews.title = insertData.msg;
    originNews.description = "";
    originNews.content = "";
    originNews.source = "";
    originNews.pubtimestr = insertData.time;
    originNews.pubtime = timestamp;
    originNews.crawltimestr = insertData.time;
    originNews.crawltime = timestamp;
    originNews.status = 0;
    originNews.shorturl = "";
    originNews.logo = "";
    originNews.labels = "";
    originNews.keyword = "";
    originNews.seq = 1;
    originNews.identity = guid();
    originNews.appname = insertData.tag;
    originNews.app_tag = insertData.tag;
    originNews.category_tag = "";
    originNews.category = "";
    originNews.restype = 4; //通知类型
    originNews.gallary = insertData.imgfilename;
    originNews.video = "";
    originNews.audio = "";

    console.log(originNews);
    //连接到表
    var collection = db.collection(tablename);
    //插入数据
    collection.insertOne(originNews,function (err,result) {
        if(err)
        {
            console.log('Error:'+ err);
            return;
        }
        //如果成功了，需要一个消息给处理队列
        callback(originNews,day);
    });
}
/**
 * 插入原始push消息数据
 * @param db mongodb数据库
 * @param callback 回调
 */
var insertPushData = function(db, insertData,callback) {
    //以时间来分表
    // var mydate = new Date();
    // var day = mydate.getFullYear()+ (mydate.getMonth() + 1 >= 10 ? mydate.getMonth() + 1 : '0' + (mydate.getMonth() + 1)) +
    //             (mydate.getDate() >= 10 ? mydate.getDate() : '0' + mydate.getDate())

    var day = insertData.time.substr(0,10);
    day = day.replace("-","");
    day = day.replace("-","");
    var tablename = "push" + day;
    //统一时间格式
    insertData.imgfilename =insertData.imgfilename.replace("_","/")
    console.log('insertData:'+ insertData.imgfilename);
    //连接到表
    var collection = db.collection(tablename);
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


        var MongoClient = mongodb.MongoClient;
        MongoClient.connect(DB_CONN_STR, function(err, db) {
            console.log("mongodb连接成功！");
            //将接收到的数据插入数据库
            insertPushData(db.db('crawlnews'), req.body,function(result) {
                console.log(result);
                insertPushDataToOriginDb(db.db('crawlnews'),req.body,function (result,day) {
                    db.close();
                    if (result!=undefined || result != null){
                        var mediaObj = {};
                        mediaObj.res_id = result.identity;
                        mediaObj.time = day;
                        mediaObj.record_time = result.crawltimestr;
                        sendToMediaQueue(mediaObj);
                    }

                    res.json({"status": "success"});
                })
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
        var tmp_path = req.param('path');
        if (tmp_path == undefined|| tmp_path == null)
            tmp_path = uploadpath;
        var filePath = path.join(tmp_path, req.query.fn);
        console.log('filePath='+filePath);
        fs.exists(filePath, function (exists) {
            var finally_path = exists ? filePath : path.join(tmp_path, "");
            console.log('finally_path='+finally_path);
            res.sendfile(finally_path);
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
