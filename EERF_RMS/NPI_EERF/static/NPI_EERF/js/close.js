// 新方法
$('#close').click(function () {
    // 标记位
    var sign = true;
    // 所有的选项数组
    var close_list = ["right_tab", "report_tab5", "report_tab3", "report_overwork", "table_delayfood"];
    // 遍历
    for (i in close_list){
        // $("#right_tab").find("tbody").find("tr").length
        l = $("#" + close_list[i]).find("tbody").find("tr").length;
        // 判断是否有数据存在
        if(l){
            // 改变标记位
            sign = false;
            // 跳出循环
            break
        }
    }
    // 没有数据调到主页
    if(sign){
        console.log("to index");
        window.location.href="/index/";
    }
});