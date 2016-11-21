/**
 * Created by Administrator on 2015/10/9.
 */
(function(){
    if(window.location.host=="cap.gongchang.com"){
        var path=window.location.pathname;
        var configList=[
            {"regex": new RegExp("\\w+"),"config":["1","0"]},
            {"regex": new RegExp("\\pub\\"),"config":["1","1"]},
            {"regex":new RegExp("/tjapis/"),"config":["1","2"]}];
        for(var i=0;i<configList.length;i++){
            if (configList[i]["regex"].exec(path)){
            gctConfig=configList[i]["config"];
        }
        }
}
})();
