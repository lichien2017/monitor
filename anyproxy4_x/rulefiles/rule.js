var http=require('http');

var nodejsQueue = "nodejsqueue"
var port = 3000;
var ruler = [];

GetRuler();//获取互联网规则

//定时执行获取规则
var myInterval=setInterval(GetRuler,1000*60*5);

module.exports = {
  summary: 'a rule to hack response',

  *beforeSendRequest(requestDetail) {
    const newRequestOptions = requestDetail.requestOptions;
      // 设置属性 rejectUnauthorized 为 false
      newRequestOptions.rejectUnauthorized = false;
      return {
        requestOptions: newRequestOptions
      };
  },

  *beforeSendResponse(requestDetail, responseDetail) {
    //今日头条
    // if(/.+?\.snssdk\.com\/api\/news\/feed\/v/i.test(requestDetail.url)){
    //     // add data to redis queue
    //     try {//防止报错退出程序
    //         HttpPost(responseDetail.response.body,requestDetail.url,requestDetail.requestData,'snssdk');//这个函数是后文定义的，将匹配到的历史消息json发送到自己的服务器
    //     }catch(e){//如果上面的正则没有匹配到，那么这个页面内容可能是公众号历史消息页面向下翻动的第二页，因为历史消息第一页是html格式的，第二页就是json格式的。
    //         console.log(e);//错误捕捉
    //     }
    // }
    // console.log(requestDetail)
    try{
        for(var i=0; i<ruler.length; i++)
        {
            var regexStr = decodeURIComponent(ruler[i].regStr);
            // console.log(regexStr);
            var regex1 = RegExp(regexStr,'i');
            if(regex1.test(requestDetail.url)) {
                console.log('规则匹配上了'+requestDetail.url);
                HttpPost(responseDetail.response.body, requestDetail.url, requestDetail.requestData, ruler[i].tag);
            }
        }
    }catch (e){
        console.log(e);//错误捕捉
    }

    return null;
  },
};
/**
 * 获取匹配规则内容
 * @constructor
 */
function GetRuler() {
    try{
        console.log('http://'+nodejsQueue+':'+port)
        http.get('http://'+nodejsQueue+':'+port,function(req,res){
            var jsonString='';
            req.on('data',function(data){
                jsonString+=data;
            });
            req.on('end',function(){
                console.log('加载规则数据');
                console.log(jsonString);
                try{
                    var jsonData = JSON.parse(jsonString);
                    if (jsonData.status == "success")
                        ruler  = JSON.parse(jsonData.data);
                }catch (e){
                    console.log(e);
                }

            });
        });
    }catch (e){
        console.log('获取规则文件失败:'+e);
    }

}
//发送json数据到服务器
function HttpPost(bodyString,url,reqData,queueTag) {//将json发送到服务器，bodyString为json内容 url请求的地址，reqData请求的数据 queueTag消息队列
    try{
        console.log('==================================HttpPost==============================');

        var data = {
            str: encodeURIComponent(bodyString),
            url: encodeURIComponent(url),
            tag: encodeURIComponent(queueTag),
            post:encodeURIComponent(reqData),
            time:new Date().getTime()
        };
        var resContent = JSON.stringify(data);

        var headers = {
            'Content-Type': 'application/json',
            'Content-Length': resContent.length
        };

        console.log(resContent);

        var options = {
            host: nodejsQueue,
            port: port,
            path: '/pkg',
            method: 'POST',
            headers: headers
        };

        var req=http.request(options,function(res){
            res.setEncoding('utf-8');

            var responseString = '';

            res.on('data', function(data) {
                responseString += data;
            });

            res.on('end', function() {
                //这里接收的参数是字符串形式,需要格式化成json格式使用
                // var resultObject = JSON.parse(responseString);
                console.log('-----resBody-----',responseString);
            });

            req.on('error', function(e) {
                // TODO: handle error.
                console.log('-----error-------',e);
            });
        });
        req.write(resContent);
        req.end();
    }catch (e){
        console.log(e);
    }

}