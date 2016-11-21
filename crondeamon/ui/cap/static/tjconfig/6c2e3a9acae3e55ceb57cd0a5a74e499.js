/**
 * Created by Administrator on 2015/10/9.
 */
(function(){
    if(window.location.host=="ch.gongchang.com"){
        var path=window.location.pathname;
        var configList=[
            {"regex": new RegExp("\\"),"config":["2","0"]}];
        for(var i=0;i<configList.length;i++){
            if (configList[i]["regex"].exec(path)){
            gctConfig=configList[i]["config"];
        }
        }
}
})();
