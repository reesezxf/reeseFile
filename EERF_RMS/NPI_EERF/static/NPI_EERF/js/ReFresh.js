// 窗口变化监听,避免resize多次执行卡顿
var resizeTimer = null;
var histor_power = document.getElementById("histor_power");
var content_box = document.getElementById("content-box");


$(window).bind('resize', function () {  //当浏览器大小变化时

    // 判断当前页面的缩放值是否大于等于150%
    if (detectZoom() >= 150 && histor_power) {
        // 刷新页面
        if (resizeTimer) clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
            window.location.reload();
        }, 500)
    }

    // 给index页面缩放大于300添加滚动条
    if (detectZoom() >= 300){
        content_box.style.overflow="auto";
    }
    else {
        content_box.removeAttribute("style");
    }

});





//获取当前页面的缩放值
function detectZoom() {
    // 初始化定义缩放值变量
    var ratio = 0,
        // 屏幕的信息对象
        screen = window.screen,
        // 浏览器的类型对象
        ua = navigator.userAgent.toLowerCase();
    // 判断屏幕缩放值非空判断
    if (window.devicePixelRatio !== undefined) {
        // window.devicePixelRatio 返回当前显示设备的物理像素分辨率(默认下值为1)
        ratio = window.devicePixelRatio;
    }
    // 否则如果没有msie浏览器
    else if (~ua.indexOf('msie')){
        // screen.deviceXDPI 返回显示屏幕的每英寸水平点数
        // screen.logicalXDPI 返回显示屏幕每英寸的水平方向的常规点数
        if (screen.deviceXDPI && screen.logicalXDPI) {
            ratio = screen.deviceXDPI / screen.logicalXDPI;
        }
    }
    // 其它浏览器
    else if (window.outerWidth !== undefined && window.innerWidth !== undefined) {
        // outerWidth 返回的是窗口元素的外部实际宽度，
        // innerWidth 返回的是窗口元素的内部实际宽度，这两个宽度都包含了滚动条在内的宽度。
        ratio = window.outerWidth / window.innerWidth;
    }

    if (ratio) {
        // 将物理像素分辨率转化为百分比(四舍五入)
        ratio = Math.round(ratio * 100);
    }

    // 返回缩放百分比
    return ratio
}

