/**
 * Created by Administrator on 2015/7/22.
 */
$(function (){
    $(window).toTop({
        showHeight: 100,
        speed: 300
    });
});

function isdisappear(obj, id) {
    var element = document.getElementById(id);
    if (obj.innerHTML == '<b>隐藏</b>') {
        obj.innerHTML = '<b>点击显示未修改部分</b>';
        element.style.display = 'none';
    }
    else {
        obj.innerHTML = '<b>隐藏</b>';
        element.style.display = 'table-row-group';
    }
}
