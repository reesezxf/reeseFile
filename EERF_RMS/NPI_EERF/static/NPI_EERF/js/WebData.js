/*
 * author:hsiao
 */
 var NightworkColumnChartDatas;
 var NightworkColumnChartTitle;
 var NightworkChart9SeriesData;
 var NightworkYAxisTitle;
 var drawChart16Datas;
 var drawChart16Title;
 var all_list;  // 全局变量 用来保存json数据

function sortNumber(a,b)
{
    // alert(a);
    return b[b.length-1] - a[a.length-1]
}

// [all_atte_data, all_atte_data8, all_atte_data9, all_atte_data11]
function meal_cost(ret){
    createTbody("table_delayfood");

    var tab_th = ret.table_name;
    var tab_weekly_th = ret.table_weeknum;
    var frist_th = "<tr>";
    for (var i = 0; i < tab_th.length; i++) {
        if (i <= 2) {
            frist_th = frist_th + "<th rowspan='2'>" + tab_th[i] + "</th>";
        } else {
            frist_th = frist_th + "<th>" + tab_th[i] + "</th>";
        }
    }
    frist_th = frist_th + "</tr>";
    $("#table_delayfood").append(frist_th);
    var seconde_th = "<tr>";
    for (var i = 0; i < tab_weekly_th.length; i++) {
        seconde_th = seconde_th + "<th>" + tab_weekly_th[i].toString().substr(0,4) + "&nbsp年&nbsp第&nbsp" + tab_weekly_th[i].toString().substr(4) + "&nbsp週</th>";
    }
    seconde_th = seconde_th + "</tr>";
    $("#table_delayfood").append(seconde_th);

    var tmp=[];
    for(var key in ret){
        if (key == "table_name" || key == "table_weeknum") {
            continue;
        }
       //key是属性,object[key]是值
       tmp.push(ret[key]);//往数组中放属性
    }
    // sort排序
    tmp.sort(sortNumber);

    // var total_table;
    for (var each_id in tmp)  {
        each_id = tmp[each_id][0];
        // console.log("each_id:", ret[each_id]);
        var totalLateMealFeeCount = 0;
        if (each_id == "table_name" || each_id == "table_weeknum") {
            continue;
        }
        var each_man = "<tr>";
        for (var j = 0; j < ret[each_id].length; j++) {
            //Count total late meal fee times
            for(var i = 3 ; i < ret[each_id].length ; i++){
                totalLateMealFeeCount = totalLateMealFeeCount + ret[each_id][i];
            }

            //Show total late meal fee count > 0 member, less than 0 don't show on page
            if(totalLateMealFeeCount > 0) {
                    each_man = each_man + "<td>" + ret[each_id][j] + "</td>";
            }
        }
        each_man = each_man + "</tr>";
        if(totalLateMealFeeCount > 0) {
            $("#table_delayfood").append(each_man);
        }
        // total_table = total_table + each_man;
    }
    // console.log("total_table:", total_table);
    // $("#table_delayfood").append(total_table);

    $("#my-modal-loading").modal("close");
};



$(function () {
    powerFunction();
    reportFormFunction();
    updatePwd();
    isVisible();
     // 新增時間篩選的功能 ---- 监听下拉框变化
     $("#select_search2").change(function() {
         // 获取下拉框的值
         var selected = $(this).children('option:selected').val();
         var valueList = ['mi', 'do', 're', 'fa'];
        // 遍历判断用户选择的值
         for (i in valueList){
             if (selected === valueList[i]){
                 // 数据替换
                 meal_cost(all_list[i]);
                 // 跳出循环
                 break;
             }
         }

     });

    /** 快照 **/
    $("#headerPicture").on('click', function(){
        var big_box = document.getElementById("big-box");
        //获取截取区域的高度和宽度
        var TargetNode = document.querySelector("#histor_power");
        // 考勤加班第一层柱状图
        var overtime_one = $("#nightwork_column_chart");
        // 考勤加班第二层折线图
        var overtime_two = $("#search_chart_contain");
        var button_con = $("#button_con");

        // 进行nightwork页面快照
      if (big_box){
            TargetNode = document.querySelector("#big-box");
            // 判断是否在第二层
            if (overtime_one.css('display') == "none" && overtime_two.css('display')  == "block"){
                button_con.css('display', 'none');
            }
        }
        var h = $(TargetNode).height();
        var w = $(TargetNode).width();
        // 判断是否在第二层
        if (overtime_one.css('display') == "none" && overtime_two.css('display')  == "block"){
            // 修改截取高度样式
            TargetNode.style.height = h + "px";
        }
        else {
            // 修改截取高度样式
            TargetNode.style.height = (h + 50) + "px";
        }

        // 分辨率高小于 700
        if (screen.height < 700){

            TargetNode.style.height = (h + 30)+ "px";
        }

        //设置 canvas 画布的宽高 是容器搞度 2倍、为了是图片清晰
        /**1.创建画布
         * 2.设置canvas 大小
         * */
        var scale = 2;
        var canvas = document.createElement("canvas");
        //这是画布整体的大小
        canvas.width = w * scale;
        canvas.height = h * scale;
        //这是绘画范围的大小
        canvas.style.width = w + "px";
        canvas.style.height = h + "px";
        canvas.style.color = "chartreuse";
        //画布缩小，将图片发大两倍
        var context = canvas.getContext("2d");
        context.scale(scale,scale);

        // 要截取全部，必须要脱离文档流 position: absolute; 否则只能截取到看到的部分。

        html2canvas($(TargetNode), {
//					allowTaint: true,
//					taintTest: false,
//					canvas: canvas,
                    useCORS: true,
                    width: w,
                    height: h,
                    windowWidth: document.body.scrollWidth,
                    windowHeight: document.body.scrollHeight,
                    x: 0,
                    y: window.pageYOffset,
            onrendered: function(canvas) {
                // 图片导出为 png 格式
                var type = 'png';
                var imgData = canvas.toDataURL(type);
                var _fixType = function(type) {
                    type = type.toLowerCase().replace(/jpg/i, 'jpeg');
                    var r = type.match(/png|jpeg|bmp|gif/)[0];
                    return 'image/' + r;
                };

                // png 替换 mime type 为了下载
                imgData = imgData.replace(_fixType(type), 'image/octet-stream');
                /**
                 * 在本地进行文件保存
                 * @param  {String} data     要保存到本地的图片数据
                 * @param  {String} filename 文件名
                 */
                var saveFile = function(data, filename) {
                //创建一个命名空间。是 a 标签
                var save_link =document.createElementNS('http://www.w3.org/1999/xhtml', 'a');
                    save_link.href = data;
                    save_link.download = filename;
                    var event = document.createEvent('MouseEvents');
                    event.initMouseEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
                    save_link.dispatchEvent(event);
                };
                // 下载后的问题名
                var filename = 'download_' + (new Date()).getTime() + '.' + type;
                // download
                saveFile(imgData, filename);
            }
        });

        // 删除添加的样式
        TargetNode.removeAttribute("style");
        button_con.css('display', 'block');

    });
    // 如果用户使用IE浏览器，就给出页面提示。

});

function saveFile(data, filename){
    var urlObject = window.URL || window.webkitURL || window;
	//去掉url的头，并转换为 long_bytes
	var long_bytes = window.atob(data.split(',')[1]);
	//处理异常,将ascii码小于0的转换为大于0
	var new_data = new ArrayBuffer(long_bytes.length);
	var ia = new Uint8Array(new_data);
	for (var i = 0; i < long_bytes.length; i++) {
		ia[i] = long_bytes.charCodeAt(i);
	}
	var export_blob = new Blob([new_data],{type : 'image/png'});
	
	var save_link = document.createElementNS('http://www.w3.org/1999/xhtml', 'a');
    save_link.href = urlObject.createObjectURL(export_blob);
    save_link.download = filename;
	
   //创建event
    var event = document.createEvent('MouseEvents');
    //初始化event
    event.initMouseEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
    //触发事件
    save_link.dispatchEvent(event);
};

function createSelect(arr) {
    var options = arr.map(function (value,index) {
        return {id:index,text:value}
    });
    // console.log('options:',options);
    $("#cluster").select2({
		data:options,
		allowClear: true,
		placeholder:'请选择资位'

	})
}

function ale() {
    //弹出一个对话框
    alert("本月份無質料！！！");
}

// 判断用户是否在页面上有操作，以此来控制cookie
function isVisible() {

    var user = Cookies.get("eerf_user");

    ifvisible.setIdleDuration(1800);

    ifvisible.on("statusChanged", function (e) {
        console.log(e.status);
    });

    ifvisible.idle(function () {
        // delete cookie set expires = olddate expires
        document.body.style.opacity = 0.5;
        Cookies.set("eerf_user", user, {expires: 600 / (24 * 60 * 60)});

    });

    ifvisible.wakeup(function () {
        document.body.style.opacity = 1;
    });
    ifvisible.onEvery(300, function () {
        Cookies.set("eerf_user", user, {expires: 30 / (24 * 60)});
    });
}

// 把页面的表格转化为excel下载下来
function tablesToExcel(table, name, filename) {

    var uri = "data:application/vnd.ms-excel;base64,"
        ,
        template = "<html xmlns:o=\"urn:schemas-microsoft-com:office:office\" xmlns:x=\"urn:schemas-microsoft-com:office:excel\" xmlns=\"http://www.w3.org/TR/REC-html40\"><head><!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets>"
        , templateend = "</x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]--></head>"
        , body = "<body>"
        , tablevar = "<table>{table"
        , tablevarend = "}</table>"
        , bodyend = "</body></html>"
        , worksheet = "<x:ExcelWorksheet><x:Name>"
        , worksheetend = "</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet>"
        , worksheetvar = "{worksheet"
        , worksheetvarend = "}"
        , base64 = function (s) {
            return window.btoa(unescape(encodeURIComponent(s)));
        }
        , format = function (s, c) {
            return s.replace(/{(\w+)}/g, function (m, p) {
                return c[p];
            });
        }
        , wstemplate = ""
        , tabletemplate = "";

    var tables = table;

    for (var i = 0; i < tables.length; ++i) {
        wstemplate += worksheet + worksheetvar + i + worksheetvarend + worksheetend;
        /*
         *  Franis addd <td></td> let two table arrange left and right
         */
        if (tables.length > 1) {
            tabletemplate += "<td>" + tablevar + i + tablevarend + "</td>";
        } else {
            tabletemplate += tablevar + i + tablevarend;
        }
    }

    /*
     * Francis add <table><tr> and </table></tr> to Conbime left_tab and right_tab to one table
     */
    if (tables.length > 1) {
        tabletemplate = "<table><tr>" + tabletemplate + "</table></tr>";
    }

    var allTemplate = template + wstemplate + templateend;
    var allWorksheet = body + tabletemplate + bodyend;
    var allOfIt = allTemplate + allWorksheet;

    var ctx = {};
    for (var j = 0; j < tables.length; ++j) {
        ctx["worksheet" + j] = name[j];
    }

    for (var k = 0; k < tables.length; ++k) {
        var exceltable;
        if (!tables[k].nodeType) exceltable = document.getElementById(tables[k]);
        ctx["table" + k] = exceltable.innerHTML;
    }

    window.location.href = uri + base64(format(allOfIt, ctx));
}

// 此函数用于考勤模块的 义务加班 和 晚班天次两个页面的柱状图上的数据  如果有小数仅保留最后一位小数
function keepTwoDecimal(num) {
    /**
     * @method
     * @param {Type} number
     * @returns
     * @desc 保留1位小数
     */
    var result = parseFloat(num);
    result = Math.round(num * 100) / 100;
    return result;
}

// 用于 power页面副标题
function getSum(arr) {
    /**
     * @method
     * @param {Type} array  [1,2,3,4,5]
     * @returns {Type} int  15
     * @desc 计算一串数字组成的数组的和
     */
    var sum = 0;
    for (var i = 0; i < arr.length; i++) {
        // console.log(arr[i]);
        sum += arr[i];
    }
    return sum;
}


// 用于离职页面和考勤加班模块的第三层
function createTbody(tableId) {
    var thisTable = document.getElementById(tableId);
    var thisTbody = thisTable.getElementsByTagName("tbody")[0];
    thisTable.removeChild(thisTbody);
    var newTbody = document.createElement("tbody");
    thisTable.appendChild(newTbody);
}

// 用于招募页面
function getTbody(tableData, tableId) {
    /**
     * @method
     * @param {Type} array
     * @returns {Type}
     * @desc  遍历数组，生成表格的每一行
     */
    var trValue = "<tr>";
    for (var j = 0; j < tableData.length; j++) {
        trValue = trValue + "<td>" + tableData[j] + "</td>";
    }
    trValue = trValue + "</tr>";
    $(tableId).append(trValue);
}

// 用于 考勤加班模块的第三层数据
function getAttendanceInfo(timestamp, leaderIndex, orderStr) {
    /**
     * @method
     * @param {Type} 时间戳，leader，页面名称用来判断数据库查询的排序
     * @returns
     * @desc 获取考勤模块四个页面的第三层的表格的数据
     */
    var data = [];
    var selectedDate = new Date(timestamp);
    var year = selectedDate.getFullYear();
    var month = selectedDate.getMonth() + 1;
    $.ajax({
        type: "POST",
        async: false,
        url: "/work_ajax/",
        dataType: "json",
        data: {"year": year, "month": month, "leaderIndex": leaderIndex, "orderStr": orderStr},
        success: function (ret) {
            // data = [];
            data = ret;
        },
        error: function () {
            alert("Error");
            console.log("getAttendanceInfo ajax fail...");
        }
    });
    return data;

}

// 用于 考勤加班模块的第四层数据
function getAttendanceInfoFour(timestamp, leaderIndex, orderStr) {
    /**
     * @method
     * @param {Type} 时间戳，leader，页面名称用来判断数据库查询的排序
     * @returns
     * @desc 获取考勤模块四个页面的第三层的表格的数据
     */
    var data = [];
    var selectedDate = new Date(timestamp);
    var year = selectedDate.getFullYear();
    var month = selectedDate.getMonth() + 1;
    $.ajax({
        type: "POST",
        async: false,
        url: "/work_section_ajax/",
        dataType: "json",
        data: {"year": year, "month": month, "leaderIndex": leaderIndex, "orderStr": orderStr},
        success: function (ret) {
            // data = [];
            data = ret;
        },
        error: function () {
            alert("Error");
            console.log("getAttendanceInfo ajax fail...");
        }
    });
    return data;

}

// 用于 报表模块的人力超时状态报表
function parseDateString(str) {
    /**
     * @method
     * @param {Type} string
     * @returns {Type} int
     * @desc 把日期字符串转化为对应的秒数
     */
    if (str == "") {
        return 0;
    }
    if (str.indexOf(",") != -1) {
        var sumSeconds = 0;
        var daysNum = str.split(",")[0].split(" ")[0];
        daysNum = parseInt(daysNum);
        var timeList = str.split(",")[1].split(":");
        var h = parseInt(timeList[0]);
        var m = parseInt(timeList[1]);
        var s = parseInt(timeList[2]);
        sumSeconds = daysNum * 86400 + h * 3600 + m * 60 + s;
        return sumSeconds;
    } else {
        var sumSeconds = 0;
        var timeList = str.split(":");
        var h = parseInt(timeList[0]);
        var m = parseInt(timeList[1]);
        var s = parseInt(timeList[2]);
        sumSeconds = h * 3600 + m * 60 + s;
        return sumSeconds;
    }
}

// 用于 报表模块的人力超时状态报表
function parseSecondsToTimeString(num) {
    /**
     * @method
     * @param {Type} int
     * @returns {Type} string
     * @desc 把 秒数 转化成时间字符串
     */
    if (num <= 86400) {
        var str = "";
        str = Math.floor((num / 3600)).toString() + ":" + Math.floor(((num % 3600) / 60)).toString() + ":" + ((num % 3600) % 60).toString();
        return str;
    } else {
        var str1 = "1 day ";
        var num2 = num - 86400;
        var str2 = Math.floor((num2 / 3600)).toString() + ":" + Math.floor(((num2 % 3600) / 60)).toString() + ":" + ((num2 % 3600) % 60).toString();
        return str1 + str2;
    }
}

// 用于 报表模块的实时人力状态报表
function cycleData(lengthOfFunction, functionKey, leaderDict) {
    /**
     * @method
     * @param {Type}
     * @returns {Type}
     * @desc 生成实时人力状态报表
     */
    var rowspanNum = 1;
    var rowspan02Num = 18;
    for (var k = 0; k < lengthOfFunction; k++) {
        var this_function_list_data = leaderDict[functionKey[k]];
        var trValue = "<tr>";
        for (var l = 0; l < this_function_list_data.length; l++) {
            /* 循环每一行数据，塞入表格中 */
            if (l == 1 || l == 3 || l == 5 || l == 7 || l == 9) {
                if (rowspanNum == 1 || rowspanNum == 3 || rowspanNum == 5 || rowspanNum == 7 || rowspanNum == 9) {
                    trValue = trValue + "<td rowspan='" + lengthOfFunction + "'>" + this_function_list_data[l] + "</td>";
                    rowspanNum = rowspanNum + 2;
                }
            } else if (l == 18 || l == 20 || l == 22 || l == 24) {
                if (rowspan02Num == 18 || rowspan02Num == 20 || rowspan02Num == 22 || rowspan02Num == 24) {
                    trValue = trValue + "<td rowspan='" + lengthOfFunction + "'>" + this_function_list_data[l] + "</td>";
                    rowspan02Num = rowspan02Num + 2;
                }
            } else {
                trValue = trValue + "<td>" + this_function_list_data[l] + "</td>";
            }
        }
        trValue = trValue + "</tr>";
        $("#right_tab_tbody").append(trValue);
    }
}

// power 页面 按照日期和资位筛选
function powerFunction() {

    $("#setting").click(function () {
        $("#mysetting").modal();
    });

    $("#power_confirm").click(function () {
        var selectedTime = document.getElementById("date").value;
        var selectedValue = $("#cluster").select2("data");
        // console.log('selectedValue:',selectedValue);
        var selectedGrade = "";
        for (var i = 0; i < selectedValue.length; i++) {
            selectedGrade += selectedValue[i].text + "_";
        }
        $.ajax({
            type: "POST",
            url: "/power_ajax/",
            data: {"selectedGrade": selectedGrade, "selectedTime": selectedTime},
            dataType: "json",
            success: function (data) {
                // console.log("success ajax_____",data);
                var categories = [], seriesMesome = [], seriesTai = [], seriesTechnician = [], seriesSpindrift = [],
                    teamDataList = [];

                for (var i = 0; i < data.length; i++) {
                    categories.push(data[i].team_leader);
                    seriesMesome.push(data[i].mesome);
                    seriesTai.push(data[i].taiwan);
                    seriesTechnician.push(data[i].technician);
                    seriesSpindrift.push(data[i].spindrift);
                    teamDataList.push(data[i].team_data);
                }
                draw_chart1(categories, seriesMesome, seriesTai, seriesTechnician, seriesSpindrift, teamDataList);
            },
            error: function () {
                alert("Error");
                console.log("fail ajax_____");
            }
        });
    });
}

// 报表模块的各种操作
function reportFormFunction() {
    //报表设置模态框


    $("#report_setting").click(function () {
        $("#reportsetting").modal();
    });
    $("#reportsetting").modal({
        show: true,
        closeViaDimmer: false
    });

    // 报表设定
    $("#report_confirm").click(function () {
        var selBU = $("#doc-select-1 option:selected").text();
        var selFrom = $("#doc-select-2 option:selected").text();
        var selTime = $("#doc_select_time").val();
        /**/
        if (selTime) {
            // console.log("seltime:",selTime);
            if (selBU == "EERF") {
                if (selFrom == "实时人力状态") {
                    $("#report_anomaly_lg").css("display","none");
                    $("#report_anomaly_tg").css("display","none");
                    $("#right_tab_tbody").html("");
                    $('#div_delayfood').css('display','none');
                    $("#left_tab_con").css("display", "block");
                    $("#right_tab_con").css("display", "block");
                    $("#report_tab3").css("display", "none");
                    $("#report_overwork").css("display", "none");
                    $("#report_tab5").css("display", "none");
                    $("#select_leader_team").css("display", "none");
                    $("#down_load").click(function () {
                        tablesToExcel(["left_tab", "right_tab"], ["first"], "myfile.xls");
                    });

                    $.ajax({
                        type: "POST",
                        url: "/report_message/",
                        data: {
                            "_time": selTime
                        },
                        dataType: "json",
                        beforeSend: function () {
                            $("#my-modal-loading").modal();
                        },
                        success: function (data) {
                            var allDataDict = eval(data);
                            // console.log("allDataDict:", allDataDict);
                            var groupList = ["Group1", "Group2", "Group3", "Magma", "EERF Total"];
                            var leaderList = [
                                ["Alex", "Vincent", "Richard Zhang", "Total"],
                                ["John", "MG", "Tai-chun", "Total"],
                                ["Richard Yu", "Andy", "Don", "Total"]
                            ];
                            var functionList = [
                                [
                                    ["FATP OTA Testing", "FATP OTA FA", "Pre-OTA"],
                                    ["OTA Chambers", "Field", "EMC/ESD", "FATP Data"],
                                    ["EE System", "OSD", "Motion sensor"]
                                ], [
                                    ["MLB CoEx & Regulatory", "FATP CoEx & Regulatory", "BBHW", "Desense"],
                                    ["RFHW"],
                                    ["MLB EE"]
                                ], [
                                    ["MLB WiPAS", "FATP WiPAS", "RF EPM WDPPM", "AP"],
                                    ["MLB RF Stations", "MLB Data", "Common"],
                                    ["EE Validation"]
                                ],
                            ];
                            for (var i = 0; i < groupList.length; i++) {
                                var groupKey = groupList[i];
                                var leaderKey = leaderList[i];
                                var groupDict = allDataDict[groupKey];

                                if (i <= 2) {
                                    /* "Group1", "Group2", "Group3" */
                                    for (var j = 0; j < leaderKey.length; j++) {
                                        var leaderDict = groupDict[leaderKey[j]];
                                        var functionKey = functionList[i][j];

                                        if (j <= 2) {
                                            /* 循环 leader 下的各个 functionTeam */
                                            var lengthOfFunction = functionKey.length;
                                            cycleData(lengthOfFunction, functionKey, leaderDict);
                                        } else {
                                            var totalTrVal = "<tr>";
                                            for (var k = 0; k < leaderDict.length; k++) {
                                                totalTrVal = totalTrVal + "<td>" + leaderDict[k] + "</td>";
                                            }
                                            totalTrVal = totalTrVal + "</tr>";
                                            $("#right_tab_tbody").append(totalTrVal);
                                        }
                                    }
                                } else {
                                    /* "Magma", "EERF Total" */
                                    var totalTrVal = "<tr>";
                                    for (var k = 0; k < groupDict.length; k++) {
                                        totalTrVal = totalTrVal + "<td>" + groupDict[k] + "</td>";
                                    }
                                    totalTrVal = totalTrVal + "</tr>";
                                    $("#right_tab_tbody").append(totalTrVal);
                                }
                                $("#my-modal-loading").modal("close");
                            }
                        },
                        error: function () {
                            alert("error");
                            $("#my-modal-loading").modal("close");
                        }
                    });

                } else if (selFrom == "人力基础总表") {
                    $('#div_delayfood').css('display','none');
                    $("#report_tab3_tbody").html("");
                    $("#left_tab_con").css("display", "none");
                    $("#right_tab_con").css("display", "none");
                    $("#report_tab3").css("display", "block");
                    $("#report_overwork").css("display", "none");
                    $("#report_tab5").css("display", "none");
                    $("#select_leader_team").css("display", "none");
                    $("#down_load").click(function () {
                        tablesToExcel(["report_tab3"], ["first"], "myfile.xls");
                    });

                    $.ajax({
                        type: "POST",
                        url: "/report_message_second/",
                        data: {
                            "_time": selTime
                        },
                        dataType: "json",
                        beforeSend: function () {
                            $("#my-modal-loading").modal();
                        },
                        success: function (data) {
                            var allDataDict = eval(data);
                            // console.log("allDataDict:",allDataDict);
                            for (keys in allDataDict) {
                                var trValue = "<tr>";
                                for (var i = 0; i < allDataDict[keys].length; i++) {
                                    trValue = trValue + "<td>" + allDataDict[keys][i] + "</td>";
                                }
                                trValue = trValue + "</tr>";
                                $("#report_tab3_tbody").append(trValue);
                            }
                            $("#my-modal-loading").modal("close");
                        },
                        error: function () {
                            alert("error");
                            $("#my-modal-loading").modal("close");
                        }
                    });
                }
                else if (selFrom == "考勤异常(陆干)") {
                    $("#report_anomaly_lg_tbody").html("");
                    $('#div_delayfood').css('display','none');
                    $("#left_tab_con").css("display", "none");
                    $("#right_tab_con").css("display", "none");
                    $("#report_tab3").css("display", "none");
                    $("#report_tab5").css("display", "none");
                    $("#report_overwork").css("display", "none");
                    $("#report_anomaly_lg").css("display","block");
                    $("#report_anomaly_tg").css("display","none");
                    $("#down_load").click(function () {
                        tablesToExcel(["report_anomaly_lg"], ["first"], "考勤异常（陆干）.xls");
                    });
                    var selectedLeader = $("#leader_select option:selected").text();
                    var selectedTeam = $("#team_select option:selected").text();

                    $.ajax({
                        type: "POST",
                        url: "/report_anomaly/",
                        dataType: "json",
                        beforeSend: function () {
                            $("#my-modal-loading").modal();
                        },
                        data: {"selectedLeader": selectedLeader, "selectedTeam": selectedTeam},
                        success: function (ret) {
                            // createTbody("report_overwork");
                            // var totalAvgOverHours = 0, totalOverHours = 0, totalMaxOverHours = 0,
                            //     totalAvgDutyHours = 0, totalDutyHours = 0, totalMaxDutyHours = 0,
                            //     totalAvgHours = 0, totalHours = 0, totalMaxHours = 0,
                            //     sumDays = 0, sumNight = 0, sumAvgCard = 0, sumMaxCard = 0,
                            //     offDuty = 0, unOffDuty = 0, eightLate = 0, eightTotal = 0, tenLate = 0, overtime_10_5 = 0, overtime_11_5 = 0, overtime_12_5 = 0;

                            for (var i = 0; i < ret.length; i++) {
                                if (ret[i].a_legal == "" || ret[i].a_department == ""){
                                    continue
                                }

                                if (ret[i].a_firstcrad == null){
                                    ret[i].a_firstcrad = ""
                                }
                                if (ret[i].a_latetime == null){
                                    ret[i].a_latetime = ""
                                }
                                if (ret[i].a_lastcard == null){
                                    ret[i].a_lastcard = ""
                                }
                                if (ret[i].a_earlytime == null){
                                    ret[i].a_earlytime = ""
                                }
                                $("#report_anomaly_lg_tbody").append("<tr><td>" + ret[i].a_legal + "</td><td>"+ ret[i].a_location + "</td><td>"+ ret[i].a_bureau + "</td><td>"+ ret[i].a_department + "</td><td>"+ ret[i].a_class + "</td><td>"+ ret[i].a_employeeid + "</td><td>" + ret[i].a_name + "</td><td>" +
                                    ret[i].a_datetime + "</td><td>" + ret[i].a_datetype + "</td><td>" + ret[i].a_type + "</td><td>" +
                                    ret[i].a_workcrad + "</td><td>" + ret[i].a_firstcrad + "</td><td>" +
                                    ret[i].a_anomalytype + "</td><td>" + ret[i].a_latetime + "</td><td>" +
                                    ret[i].a_replytype + "</td><td>" + ret[i].a_closedcard + "</td><td>" +
                                    ret[i].a_lastcard + "</td><td>" + ret[i].a_anomalytype2 + "</td><td>" + ret[i].a_earlytime + "</td><td>" + ret[i].a_replytype2 + "</td></tr>" );
                            }
                            $("#my-modal-loading").modal("close");
                        },
                        error: function () {
                            alert("Error");
                            $("#my-modal-loading").modal("close");
                            console.log("report_message_third ajax fail.....");
                        }
                    });
                }

                else if (selFrom == "考勤异常(台干)") {
                    $("#report_anomaly_tg_tbody").html("");
                    $('#div_delayfood').css('display','none');
                    $("#left_tab_con").css("display", "none");
                    $("#right_tab_con").css("display", "none");
                    $("#report_tab3").css("display", "none");
                    $("#report_tab5").css("display", "none");
                    $("#report_overwork").css("display", "none");
                    $("#report_anomaly_lg").css("display","none");
                    $("#report_anomaly_tg").css("display","block");
                    $("#down_load").click(function () {
                        tablesToExcel(["report_anomaly_tg"], ["first"], "考勤异常（台干）.xls");
                    });
                    var selectedLeader = $("#leader_select option:selected").text();
                    var selectedTeam = $("#team_select option:selected").text();

                    $.ajax({
                        type: "POST",
                        url: "/report_anomaly/",
                        dataType: "json",
                        beforeSend: function () {
                            $("#my-modal-loading").modal();
                        },
                        data: {"selectedLeader": selectedLeader, "selectedTeam": selectedTeam},
                        success: function (ret) {
                            // createTbody("report_overwork");
                            // var totalAvgOverHours = 0, totalOverHours = 0, totalMaxOverHours = 0,
                            //     totalAvgDutyHours = 0, totalDutyHours = 0, totalMaxDutyHours = 0,
                            //     totalAvgHours = 0, totalHours = 0, totalMaxHours = 0,
                            //     sumDays = 0, sumNight = 0, sumAvgCard = 0, sumMaxCard = 0,
                            //     offDuty = 0, unOffDuty = 0, eightLate = 0, eightTotal = 0, tenLate = 0, overtime_10_5 = 0, overtime_11_5 = 0, overtime_12_5 = 0;

                            for (var i = 0; i < ret.length; i++) {
                                if (ret[i].a_legal == "" && ret[i].a_department == "") {
                                    if (ret[i].a_firstcrad == null) {
                                        ret[i].a_firstcrad = ""
                                    }
                                    if (ret[i].a_latetime == null) {
                                        ret[i].a_latetime = ""
                                    }
                                    if (ret[i].a_lastcard == null) {
                                        ret[i].a_lastcard = ""
                                    }
                                    if (ret[i].a_earlytime == null) {
                                        ret[i].a_earlytime = ""
                                    }
                                    $("#report_anomaly_tg_tbody").append("<tr><td>" + ret[i].a_location + "</td><td>" + ret[i].a_bureau + "</td><td>" + ret[i].a_class + "</td><td>" + ret[i].a_employeeid + "</td><td>" + ret[i].a_name + "</td><td>" +
                                        ret[i].a_datetime + "</td><td>" + ret[i].a_datetype + "</td><td>" + ret[i].a_type + "</td><td>" +
                                        ret[i].a_workcrad + "</td><td>" + ret[i].a_firstcrad + "</td><td>" +
                                        ret[i].a_anomalytype + "</td><td>" + ret[i].a_latetime + "</td><td>" +
                                        ret[i].a_replytype + "</td><td>" + ret[i].a_closedcard + "</td><td>" +
                                        ret[i].a_lastcard + "</td><td>" + ret[i].a_anomalytype2 + "</td><td>" + ret[i].a_earlytime + "</td><td>" + ret[i].a_replytype2 + "</td></tr>");
                                }
                            }
                            $("#my-modal-loading").modal("close");
                        },
                        error: function () {
                            alert("Error");
                            $("#my-modal-loading").modal("close");
                            console.log("report_message_third ajax fail.....");
                        }
                    });
                }
                else if (selFrom == "月人力超时状态") {
                    $("#report_anomaly_lg").css("display","none");
                    $("#report_anomaly_tg").css("display","none");
                    $("#report_tab3_tbody").html("");
                    $('#div_delayfood').css('display','none');
                    $("#left_tab_con").css("display", "none");
                    $("#right_tab_con").css("display", "none");
                    $("#report_tab3").css("display", "none");
                    $("#report_tab5").css("display", "none");
                    $("#report_overwork").css("display", "block");
                    $("#down_load").click(function () {
                        tablesToExcel(["report_overwork"], ["first"], "myfile.xls");
                    });

                    var selectedLeader = $("#leader_select option:selected").text();
                    var selectedTeam = $("#team_select option:selected").text();

                    $.ajax({
                        type: "POST",
                        url: "/report_message_third/",
                        dataType: "json",
                        beforeSend: function () {
                            $("#my-modal-loading").modal();
                        },
                        data: {"selectedLeader": selectedLeader, "selectedTeam": selectedTeam, "_time": selTime},
                        success: function (ret) {
                            createTbody("report_overwork");
                            var totalAvgOverHours = 0, totalOverHours = 0, totalMaxOverHours = 0,
                                totalAvgDutyHours = 0, totalDutyHours = 0, totalMaxDutyHours = 0,
                                totalAvgHours = 0, totalHours = 0, totalMaxHours = 0,
                                sumDays = 0, sumNight = 0, sumAvgCard = 0, sumMaxCard = 0,
                                offDuty = 0, unOffDuty = 0, eightLate = 0, eightTotal = 0, tenLate = 0, overtime_10_5 = 0, overtime_11_5 = 0, overtime_12_5 = 0;

                            for (var i = 0; i < ret.length; i++) {
                                totalAvgOverHours += parseFloat(ret[i].a_avgoverhours);
                                totalAvgDutyHours += parseFloat(ret[i].a_avgdutyhours);
                                totalAvgHours += parseFloat(ret[i].a_avghours);
                                totalOverHours += parseFloat(ret[i].a_totaloverhours);
                                totalDutyHours += parseFloat(ret[i].a_totaldutyhours);
                                totalHours += parseFloat(ret[i].a_totalhours);
                                totalMaxOverHours += parseFloat(ret[i].a_maxoverhours);
                                totalMaxDutyHours += parseFloat(ret[i].a_maxdutyhours);
                                totalMaxHours += parseFloat(ret[i].a_maxhours);
                                sumDays += ret[i].a_totaldays;
                                sumNight += ret[i].a_nightnum;
                                sumAvgCard += parseDateString(ret[i].a_avglastcard);
                                sumMaxCard += parseDateString(ret[i].a_maxlastcard);
                                offDuty += parseFloat(ret[i].a_offduty);
                                unOffDuty += parseFloat(ret[i].a_unoffduty);
                                eightLate += parseFloat(ret[i].a_eightlate);
                                eightTotal += parseFloat(ret[i].a_eighttotal);
                                tenLate += parseFloat(ret[i].a_tenlate);
                                overtime_10_5 += parseFloat(ret[i].p_10_5_hours);
                                overtime_11_5 += parseFloat(ret[i].p_11_5_hours);
                                overtime_12_5 += parseFloat(ret[i].p_12_5_hours);


                                $("#report_overwork").append("<tr><td>" + ret[i].a_employee + "</td><td>" + ret[i].a_name + "</td><td>" +
                                    ret[i].a_leader + "</td><td>" + ret[i].a_team+ "</td><td>" + ret[i].a_interval + "</td><td>" +
                                    parseFloat(ret[i].a_avgoverhours).toFixed(2) + "</td><td>" + parseFloat(ret[i].a_totaloverhours).toFixed(2) + "</td><td>" +
                                    parseFloat(ret[i].a_avghours).toFixed(2) + "</td><td>" + parseFloat(ret[i].a_totalhours).toFixed(2) + "</td><td>" +
                                    ret[i].a_totaldays + "</td><td>" + ret[i].a_nightnum + "</td><td>" +
                                    ret[i].a_offduty + "</td><td>" + ret[i].a_unoffduty + "</td><td>" + ret[i].p_10_5_hours + "</td><td>" + ret[i].p_11_5_hours + "</td><td>" + ret[i].p_12_5_hours + "</td><td>" +
                                    parseFloat(ret[i].a_eighttotal).toFixed(2) + "</td></tr>");
                            }
                            var avgTotalAvgDutyHours = (totalAvgDutyHours / ret.length).toFixed(2);  // 部门平均的 平均义务时长
                            var avgTotalDutyHours = (totalDutyHours / ret.length).toFixed(2);    // 部门平均的 总义务
                            var avgTotalMaxDutyHours = (totalMaxDutyHours / ret.length).toFixed(2); // 部门平均的 最大义务时长

                            var avgTotalOverHours = (totalOverHours / ret.length).toFixed(2);  //平均的 总超时
                            var avgTotalAvgOverHours = (totalAvgOverHours / ret.length).toFixed(2);   // 部门平均的  平均超时
                            var avgTotalMaxOverHours = (totalMaxOverHours / ret.length).toFixed(2); // 部门平均的 最大超时时长

                            var avgTotalMaxHours = (totalMaxHours / ret.length).toFixed(2);   // 部门平均的 最大工作时长
                            var avgTotalAvgHours = (totalAvgHours / ret.length).toFixed(2);     //部门平均的 平均工作时长
                            var avgTotalHours = (totalHours / ret.length).toFixed(2);   // 部门平均的 总工作时长

                            var avgWorkDays = (sumDays / ret.length).toFixed(2);
                            var avgNightWork = (sumNight / ret.length).toFixed(2);

                            var avgOffDuty = (offDuty / ret.length).toFixed(2);
                            var avgUnOffDuty = (unOffDuty / ret.length).toFixed(2);
                            var avgOvertime_10_5 = (overtime_10_5 / ret.length).toFixed(2);
                            var avgOvertime_11_5 = (overtime_11_5 / ret.length).toFixed(2);
                            var avgOvertime_12_5 = (overtime_12_5 / ret.length).toFixed(2);
                            var avgEightTotal = (eightTotal / ret.length).toFixed(2);

                            var avgAvgCard = parseSecondsToTimeString(Math.floor(sumAvgCard / ret.length));
                            var avgMaxCard = parseSecondsToTimeString(Math.floor(sumMaxCard / ret.length));

                            $("#report_overwork").append("<tr><td colspan = 5>Average</td><td>" +
                                avgTotalAvgOverHours + "</td><td>" + avgTotalOverHours + "</td><td>" + avgTotalAvgHours + "</td><td>" +
                                avgTotalHours + "</td><td>" + avgWorkDays + "</td><td>" + avgNightWork + "</td><td>" +
                                avgOffDuty + "</td><td>" + avgUnOffDuty + "</td><td>" + avgOvertime_10_5 + "</td><td>" + avgOvertime_11_5 + "</td><td>" + avgOvertime_12_5 + "</td><td>" +
                                avgEightTotal + "</td></tr>");
                            $("#my-modal-loading").modal("close");
                        },
                        error: function () {
                            alert("Error");
                            $("#my-modal-loading").modal("close");
                            console.log("report_message_third ajax fail.....");
                        }
                    });

                }
                else if (selFrom == "实时超时状态") {
                    $("#report_tab5_tbody").html("");
                    $("#report_anomaly_lg").css("display","none");
                    $("#report_anomaly_tg").css("display","none");
                    $("#left_tab_con").css("display", "none");
                    $("#right_tab_con").css("display", "none");
                    $("#report_tab3").css("display", "none");
                    $("#report_overwork").css("display", "none");
                    $('#div_delayfood').css('display','none');
                    $("#report_tab5").css("display", "block");
                    $("#down_load").click(function () {
                        tablesToExcel(["report_tab5"], ["first"], "myfile.xls");
                    });

                    var selectedLeader = $("#leader_select option:selected").text();
                    var selectedTeam = $("#team_select option:selected").text();

                    $.ajax({
                        type: "POST",
                        url: "/report_message_four/",
                        dataType: "json",
                        beforeSend: function () {
                            $("#my-modal-loading").modal();
                        },
                        data: {"selectedLeader": selectedLeader, "selectedTeam": selectedTeam, "_time": selTime},
                        success: function (ret) {
                            // console.log('ret:', ret);
                            createTbody("report_tab5");
                            var totalAvgOverHours = 0, totalOverHours = 0, totalMaxOverHours = 0,
                                totalAvgDutyHours = 0, totalDutyHours = 0, totalMaxDutyHours = 0,
                                totalAvgHours = 0, totalHours = 0, totalMaxHours = 0,
                                sumDays = 0, sumNight = 0, sumAvgCard = 0, sumMaxCard = 0,
                                offDuty = 0, unOffDuty = 0, eightLate = 0, eightTotal = 0, tenLate = 0, overtime_10_5 = 0, overtime_11_5 = 0, overtime_12_5 = 0;

                            for (var i = 0; i < ret.length; i++) {
                                totalAvgOverHours += parseFloat(ret[i].a_avgoverhours);
                                totalAvgDutyHours += parseFloat(ret[i].a_avgdutyhours);
                                totalAvgHours += parseFloat(ret[i].a_avghours);
                                totalOverHours += parseFloat(ret[i].a_totaloverhours);
                                totalDutyHours += parseFloat(ret[i].a_totaldutyhours);
                                totalHours += parseFloat(ret[i].a_totalhours);
                                totalMaxOverHours += parseFloat(ret[i].a_maxoverhours);
                                totalMaxDutyHours += parseFloat(ret[i].a_maxdutyhours);
                                totalMaxHours += parseFloat(ret[i].a_maxhours);
                                sumDays += ret[i].a_totaldays;
                                sumNight += ret[i].a_nightnum;
                                sumAvgCard += parseDateString(ret[i].a_avglastcard);
                                sumMaxCard += parseDateString(ret[i].a_maxlastcard);
                                offDuty += parseFloat(ret[i].a_offduty);
                                unOffDuty += parseFloat(ret[i].a_unoffduty);
                                eightLate += parseFloat(ret[i].a_eightlate);
                                eightTotal += parseFloat(ret[i].a_eighttotal);
                                tenLate += parseFloat(ret[i].a_tenlate);
                                overtime_10_5 += parseFloat(ret[i].p_10_5_hours);
                                overtime_11_5 += parseFloat(ret[i].p_11_5_hours);
                                overtime_12_5 += parseFloat(ret[i].p_12_5_hours);


                                $("#report_tab5").append("<tr><td>" + ret[i].a_employee + "</td><td>" + ret[i].a_name + "</td><td>" +
                                    ret[i].a_leader + "</td><td>" + ret[i].a_team+ "</td><td>" + ret[i].a_interval + "</td><td>" +
                                    parseFloat(ret[i].a_avgoverhours).toFixed(2) + "</td><td>" + parseFloat(ret[i].a_totaloverhours).toFixed(2) + "</td><td>" +
                                    parseFloat(ret[i].a_avghours).toFixed(2) + "</td><td>" + parseFloat(ret[i].a_totalhours).toFixed(2) + "</td><td>" +
                                    ret[i].a_totaldays + "</td><td>" + ret[i].a_nightnum + "</td><td>" +
                                    ret[i].a_offduty + "</td><td>" + ret[i].a_unoffduty + "</td><td>" + ret[i].p_10_5_hours + "</td><td>" + ret[i].p_11_5_hours + "</td><td>" + ret[i].p_12_5_hours + "</td><td>" +
                                    parseFloat(ret[i].a_eighttotal).toFixed(2) + "</td></tr>");
                            }
                            var avgTotalAvgDutyHours = (totalAvgDutyHours / ret.length).toFixed(2);  // 部门平均的 平均义务时长
                            var avgTotalDutyHours = (totalDutyHours / ret.length).toFixed(2);    // 部门平均的 总义务
                            var avgTotalMaxDutyHours = (totalMaxDutyHours / ret.length).toFixed(2); // 部门平均的 最大义务时长

                            var avgTotalOverHours = (totalOverHours / ret.length).toFixed(2);  //平均的 总超时
                            var avgTotalAvgOverHours = (totalAvgOverHours / ret.length).toFixed(2);   // 部门平均的  平均超时
                            var avgTotalMaxOverHours = (totalMaxOverHours / ret.length).toFixed(2); // 部门平均的 最大超时时长

                            var avgTotalMaxHours = (totalMaxHours / ret.length).toFixed(2);   // 部门平均的 最大工作时长
                            var avgTotalAvgHours = (totalAvgHours / ret.length).toFixed(2);     //部门平均的 平均工作时长
                            var avgTotalHours = (totalHours / ret.length).toFixed(2);   // 部门平均的 总工作时长

                            var avgWorkDays = (sumDays / ret.length).toFixed(2);
                            var avgNightWork = (sumNight / ret.length).toFixed(2);

                            var avgOffDuty = (offDuty / ret.length).toFixed(2);
                            var avgUnOffDuty = (unOffDuty / ret.length).toFixed(2);
                            var avgOvertime_10_5 = (overtime_10_5 / ret.length).toFixed(2);
                            var avgOvertime_11_5 = (overtime_11_5 / ret.length).toFixed(2);
                            var avgOvertime_12_5 = (overtime_12_5 / ret.length).toFixed(2);
                            var avgEightTotal = (eightTotal / ret.length).toFixed(2);

                            var avgAvgCard = parseSecondsToTimeString(Math.floor(sumAvgCard / ret.length));
                            var avgMaxCard = parseSecondsToTimeString(Math.floor(sumMaxCard / ret.length));

                            $("#report_tab5").append("<tr><td colspan = 5>Average</td><td>" +
                                avgTotalAvgOverHours + "</td><td>" + avgTotalOverHours + "</td><td>" + avgTotalAvgHours + "</td><td>" +
                                avgTotalHours + "</td><td>" + avgWorkDays + "</td><td>" + avgNightWork + "</td><td>" +
                                avgOffDuty + "</td><td>" + avgUnOffDuty + "</td><td>" + avgOvertime_10_5 + "</td><td>" + avgOvertime_11_5 + "</td><td>" + avgOvertime_12_5 + "</td><td>" +
                                avgEightTotal + "</td></tr>");
                            $("#my-modal-loading").modal("close");
                        },
                        error: function () {
                            alert("Error");
                            $("#my-modal-loading").modal("close");
                            console.log("report_message_third ajax fail.....");
                        }
                    });

                } else if (selFrom == "误餐费") {
                    $("#report_tab3_tbody").html("");
                    $("#report_anomaly_lg").css("display","none");
                    $("#report_anomaly_tg").css("display","none");
                    $("#left_tab_con").css("display", "none");
                    $("#right_tab_con").css("display", "none");
                    $("#report_tab3").css("display", "none");
                    $("#report_overwork").css("display", "none");
                    $("#report_tab5").css("display", "none");
                    // 显示误餐费报表
                    $('#div_delayfood').css('display','block');
                    $('#table_delayfood').css('display','block');
                    var title_date = $("#start_select_time").val() + ' ~ ' + $("#end_select_time").val();
                    $('#title_date').text(title_date + '的誤餐費');
                    $("#down_load").click(function () {
                        tablesToExcel(["table_delayfood"], ["first"], "myfile.xls");
                    });
                    var selectedLeader = $("#leader_select option:selected").text();
                    var selectedTeam = $("#team_select option:selected").text();
                    var startTime = $("#start_select_time").val();
                    var endTime = $("#end_select_time").val();

                    $.ajax({
                        type: "POST",
                        url: "/report_message_five/",
                        dataType: "json",
                        beforeSend: function () {
                            $("#my-modal-loading").modal();
                        },
                        data: {"selectedLeader": selectedLeader, "selectedTeam": selectedTeam, "startTime": startTime, "endTime": endTime},
                        success: function (ret) {
                            // 储存json数据
                            all_list = ret;
                            meal_cost(ret[2]);
                        },
                        error: function () {
                            alert("Error");
                            $("#my-modal-loading").modal("close");
                            console.log("report_message_third ajax fail.....");
                        }
                    });

                }else {
                    alert("Wrong Choice!!!");
                }
            } else {
                alert("Wrong Choice!!!");
            }
        } else {
            alert("Please Select TimeDate!!!");
        }

    });
}



//登陆页面修改密码时 页面元素的消失或者可见
function updatePwd() {
    $("#change_pass").click(function () {
        if ($("#change_pass").prop("checked")) {
            $("#name_con").css("display", "none");
            $("#pass_con").css("display", "none");
            $("#submit_btn").css("display", "none");
            $("#change_pass_con1").css("display", "block");
            $("#change_pass_con2").css("display", "block");
            $("#confirm_pass_btn").css("display", "block");
            $("#change_name_con").css("display", "block");

        } else {
            $("#name_con").css("display", "block");
            $("#pass_con").css("display", "block");
            $("#submit_btn").css("display", "block");
            $("#submit_btn").css("margin-left", "20%");
            $("#change_pass_con1").css("display", "none");
            $("#change_pass_con2").css("display", "none");
            $("#confirm_pass_btn").css("display", "none");
            $("#change_name_con").css("display", "none");
        }
    });

    //修改密码事件
    $("#confirm_pass_btn").click(function () {
        var update_user = $("#update_username").val();
        console.log("update_user", update_user);
        var old_pwd = $("#old_pwd").val();
        var new_pwd = $("#new_pwd").val();
        if (update_user == "") {
            $("#gh").css("display", "block");
            $("#update_username").bind("input propertychange", function () {
                $("#gh").css("display", "none");
                $("#icon_gh").css("top", "35%");
            });
            $("#icon_gh").css("top", "22%");
        } else if (old_pwd == "") {
            $("#jmm").css("display", "block");
            $("#change_pass_con1").bind("input propertychange", function () {
                $("#jmm").css("display", "none");
                $("#icon_jmm").css("top", "35%");
            });
            $("#icon_jmm").css("top", "22%");
        } else if (new_pwd == "") {
            $("#xmm").css("display", "block");
            $("#change_pass_con2").bind("input propertychange", function () {
                $("#xmm").css("display", "none");
                $("#icon_xmm").css("top", "35%");
            });
            $("#icon_xmm").css("top", "22%");
        } else {
            $.ajax({
                type: "POST",
                url: "/update_pwd/",
                data: {"update_user": update_user, "old_pwd": old_pwd, "new_pwd": new_pwd},
                dataType: "json",
                success: function (data) {
                    if (data == "success") {
                        alert("修改成功");
                        $("#name_con").css("display", "block");
                        $("#pass_con").css("display", "block");
                        $("#submit_btn").css("display", "block");
                        $("#submit_btn").css("margin-left", "20%");
                        $("#change_pass_con1").css("display", "none");
                        $("#change_pass_con2").css("display", "none");
                        $("#confirm_pass_btn").css("display", "none");
                        $("#change_name_con").css("display", "none");
                        $("#change_pass").prop("checked", false);
                    } else if (data == "old_pwd") {
                        alert("旧密码错误");
                        $("#name_con").css("display", "none");
                        $("#pass_con").css("display", "none");
                        $("#submit_btn").css("display", "none");
                        $("#change_pass_con1").css("display", "block");
                        $("#change_pass_con2").css("display", "block");
                        $("#confirm_pass_btn").css("display", "block");
                        $("#change_name_con").css("display", "block");
                        $("#change_pass").prop("checked", true);
                    } else {
                        alert("用户不存在");
                        $("#name_con").css("display", "none");
                        $("#pass_con").css("display", "none");
                        $("#submit_btn").css("display", "none");
                        $("#change_pass_con1").css("display", "block");
                        $("#change_pass_con2").css("display", "block");
                        $("#confirm_pass_btn").css("display", "block");
                        $("#change_name_con").css("display", "block");
                        $("#change_pass").prop("checked", true);
                    }
                },
                error: function (err) {
                    console.log("error___", err);
                    alert("修改失败");
                }
            });
        }

    });
}

/**
 * 人力模块的5个页面
 * power：draw_chart1(),draw_chart2(),draw_chart3()
 * historypower:draw_chart4()
 * unitspower:draw_chart13(),draw_chart14(),draw_chart15()
 * recruit: draw_chart5(), draw_chart6(),draw_chart17()
 * dimission: draw_chart8(),draw_chart7(), draw_chart19()
 */

// power 页面的 实时人力概览
function draw_chart1(x_categories, seriesMesome, seriesTai, seriesTechnician, seriesSpindrift, teamDataList) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */

    var all_num = getSum(seriesTai) + getSum(seriesMesome) + getSum(seriesTechnician) + getSum(seriesSpindrift);
    $("#power_column_chart").highcharts({
        chart: {
            type: "column",
            backgroundColor: "rgba(0,0,0,0)"
        },
        title: {
            text: "实时人力概览",
            style: {
                fontSize: "20px",
                color: "#333"
            }
        },
        subtitle: {
            text: "总人数:" + all_num + "      " + "中干:" + getSum(seriesMesome) + "    " + "台干:" + getSum(seriesTai) + "    " + "员级:" + getSum(seriesTechnician) + "    " + "浪花:" + getSum(seriesSpindrift),
            style: {
                fontSize: "16px",
                color: "#d24d4d",
                whiteSpace: "pre"
            }
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "Real-time-human-resources",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        xAxis: {

            categories: x_categories,

            labels: {
                style: {
                    fontSize: 16,
                    color: "#333"
                }
            },
            plotBands: [{
                color: "#FFFFCC",

                from: -0.5,
                to: 2.5,
                zIndex: 2,
                label: {
                    text: "Group1",
                    verticalAlign: "top",
                    style: {
                        fontSize: "16px",
                        fontWeight: 600,

                    }
                }
            }, {
                color: "#CCFFFF",
                from: 2.5,
                to: 5.5,
                zIndex: 2,
                label: {
                    text: "Group2",
                    verticalAlign: "top",
                    style: {
                        fontSize: "16px",
                        fontWeight: 600,

                    }

                }
            },
                {
                    color: "#FFCCCC",
                    from: 5.5,
                    to: 8.5,
                    zIndex: 2,
                    label: {
                        text: "Group3",
                        verticalAlign: "top",
                        style: {
                            fontSize: "16px",
                            fontWeight: 600,

                        }
                    }

                }],

            crosshair: true
        },
        yAxis: {
            min: 0,
            title: {
                text: "人数(人)",
                style: {
                    fontSize: 16,
                    color: "#333"
                }
            },
            labels: {
                style: {
                    fontSize: 14,
                    color: "#333"
                }
            }
        },
        legend: {
            itemStyle: {
                "fontSize": "16px"
            }
        },
        credits: {
            enabled: false
        },
        tooltip: {
            enabled: false,
            headerFormat: "<span style=\"font-size:10px\">{point.key}</span><table>",
            pointFormat: "<tr><td style=\"color:{series.color};padding:0\">{series.name}: </td>" +
            "<td style=\"padding:0\"><b>{point.y} mm</b></td></tr>",
            footerFormat: "</table>",
            shared: true,
            useHTML: true
        },
        plotOptions: {
            column: {
                borderWidth: 0,
                cursor: "pointer",
                dataLabels: {
                    enabled: true,
                    style: {
                        // fontWeight: 'bold',
                        fontSize: "11px",
                        color: "#003399"
                    }
                },
                point: {
                    events: {
                        click: function () {

                            var teamData = teamDataList[this.index];
                            $("#power_column_chart").css("display", "none");
                            $("#setting").css("display", "none");
                            $("#chart_dron_down").css("display", "block");
                            draw_chart2(teamData);
                            draw_chart3(teamData);
                        }
                    }
                }
            }
        },
        series: [{
            name: "中干",
            data: seriesMesome
        }, {
            name: "台干",
            data: seriesTai
        }, {
            name: "员级",
            data: seriesTechnician
        }, {
            name: "浪花",
            data: seriesSpindrift
        }]
    });
    //返回总人力
    $("#off_chart_container").click(function () {
        // draw_chart1(x_categories, seriesMesome, seriesTai, seriesTechnician, seriesSpindrift, teamDataList);
        $("#power_column_chart").css("display", "block");
        $("#chart_dron_down").css("display", "none");
        $("#setting").css("display", "block");
    });

};

// power 页面 每个leader下属的各个function team人数柱形图
function draw_chart2(teamData) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    var chart2SeriesData = [];
    for (var i = 0; i < teamData.length; i++) {
        var eachTeamSeries = {};
        eachTeamSeries.name = teamData[i].name;
        eachTeamSeries.data = [];
        eachTeamSeries.data.push(teamData[i].mesome);
        eachTeamSeries.data.push(teamData[i].taiwan);
        eachTeamSeries.data.push(teamData[i].technician);
        eachTeamSeries.data.push(teamData[i].spindrift);
        chart2SeriesData.push(eachTeamSeries);
    }
    $("#power_time_manpower_column").highcharts({
        chart: {
            type: "column",
            backgroundColor: "rgba(0,0,0,0)"
        },
        title: {
            text: "实时人力状况"
        },
        xAxis: {
            categories: [
                "中干",
                "台干",
                "员级",
                "浪花"
            ],
            crosshair: true
        },
        yAxis: {
            min: 0,
            title: {
                text: "人数(人)"
            }
        },
        credits: {
            enabled: false
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "实时人力状况",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        tooltip: {
            enabled: false,
            headerFormat: "<span style=\"font-size:10px\">{point.key}</span><table>",
            pointFormat: "<tr><td style=\"color:{series.color};padding:0\">{series.name}: </td>" +
            "<td style=\"padding:0\"><b>{point.y} </b></td></tr>",
            footerFormat: "</table>",
            shared: true,
            useHTML: true
        },
        plotOptions: {
            column: {
                borderWidth: 0,
                dataLabels: {
                    enabled: true,
                    style: {
                        // fontWeight: 'bold',
                        fontSize: "11px",
                        color: "#003399"
                    }
                }
            }
        },
        series: chart2SeriesData
    });
}

// power 页面 每个leader下属的各个function team人数 圆饼图
function draw_chart3(teamData) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    var chart3SeriesData = [];
    for (var i = 0; i < teamData.length; i++) {
        var eachTeanSeriesData = [];
        eachTeanSeriesData.push(teamData[i].name);
        eachTeanSeriesData.push(teamData[i].total);
        chart3SeriesData.push(eachTeanSeriesData);
    }
    $("#power_time_manpower_pie").highcharts({
        chart: {
            // type: 'column',
            backgroundColor: "rgba(0,0,0,0)",
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        credits: {
            enabled: false
        },
        title: {
            text: "实时人力分布"
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "实时人力分布",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        tooltip: {
            headerFormat: "{series.name}<br>",
            pointFormat: "{point.name}: <b>{point.percentage:.1f}% </b>"
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: "pointer",
                dataLabels: {
                    enabled: true,
                    format: " <br>{point.name}:{point.y},{point.percentage:.1f}%",
                    // distance:-60,
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || "black"
                    }
                }
            }
        },
        series: [{
            type: "pie",
            name: "人力状况分布",
            data: chart3SeriesData,

        }]
    });
};

// historypower页面 -历年人力
function draw_chart4(seriesData) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    Highcharts.setOptions({
        lang: {
            shortMonths: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
    });

    $("#historypower_line_chart").highcharts("StockChart", {
        rangeSelector: {
            allButtonsEnabled: true,
            buttons: [
                {
                    type: "month",
                    count: 6,
                    text: "6m"
                },
                {
                    type: "year",
                    count: 1,
                    text: "1y"
                },
                {
                    type: "all",
                    text: "All"
                }
            ],
            selected: 1
        },
        chart: {
            backgroundColor: "rgba(0,0,0,0)"
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "历年人力",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        title: {
            text: "历年人力",
            style: {
                fontSize: "20px",
            }
        },
        subtitle: {
            text: "2017年8月EE併入RF"
        },
        credits: {
            enabled: false
        },
        legend: {
            enabled: true
        },
        xAxis: {
            type: "datetime",
            dateTimeLabelFormats: {
                day: "%Y<br/>%m-%d",
                month: "%Y-%m",
                year: "%Y"
            }
        },
        yAxis: {
            labels: {
                formatter: function () {
                    return this.value;
                }
            },
            title: {
                text: "时数(h)"
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true,
                    crop: false,
                    allowOverlap: true
                    //overflow: 'none',
                    //format:'{point.y:.2f}%',
                }
            },
            series: {
                showInLegend: true
            }
        },
        tooltip: {
            xDateFormat: "%B %Y" + "<br/>" + "%Y-%m-%d",
        },
        series: seriesData
    });

}

//UnitsPower 编制人力
function draw_chart13(data, authority) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    var chart13SeriesData = [];
    for (var i = 0; i < data.length; i++) {
        var eachSeries = {};
        eachSeries.name = data[i].pleader;
        eachSeries.data = [];
        for (var j = 0; j < data[i].num_data.length; j++) {
            var eachList = [];
            eachList.push(data[i].num_data[j].leader_name);
            eachList.push(data[i].num_data[j].num);
            eachSeries.data.push(eachList);
        }
        chart13SeriesData.push(eachSeries);
    }
    $("#unitspower_column_chart").highcharts({
        chart: {
            type: "column",
            backgroundColor: "rgba(0,0,0,0)"
        },
        title: {
            text: "编制人力",
            style: {
                fontSize: "20px",
                color: "#333"
            }
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "编制人力",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        // 横坐标显示
        xAxis: {
            type: "category",

            labels: {
                style: {
                    fontSize: 16,
                    color: "#333"
                }
            },
            crosshair: true
        },
        yAxis: {
            min: 0,
            title: {
                text: "人数(人)",
                style: {
                    fontSize: 16,
                    color: "#333"
                }
            },
            labels: {
                style: {
                    fontSize: 14,
                    color: "#333"
                }
            }
        },
        legend: {
            itemStyle: {
                "fontSize": "16px"
            }
        },
        credits: {
            enabled: false
        },
        tooltip: {
            enabled: false,
            headerFormat: "<span style=\"font-size:10px\">{point.key}</span><table>",
            pointFormat: "<tr><td style=\"color:{series.color};padding:0\">{series.name}: </td>" +
            "<td style=\"padding:0\"><b>{point.y} </b></td></tr>",
            footerFormat: "</table>",
            shared: true,
            useHTML: true
        },
        plotOptions: {
            column: {
                borderWidth: 0,
                dataLabels: {
                    allowOverlap: "0",
                    enabled: true,
                    crop: false,
                    overflow: "none",
                    format: "{point.y}",
                },
                cursor: "pointer",
                point: {
                    events: {
                        click: function () {
                            $("#unitspower_column_chart").css("display", "none");
                            $("#chart_dron_down").css("display", "block");
                            $("#unitssetting").css("display", "none");
                            var seriesChart15 = [];

                            for (var k = 0; k < data.length; k++) {
                                var series_ = {};
                                series_.name = data[k].pleader;
                                series_.data = [];
                                for (var l = 0; l < data[k].num_data[this.index].team_data.length; l++) {
                                    var eachSeries_ = [];
                                    eachSeries_.push(data[k].num_data[this.index].team_data[l].team_name);
                                    eachSeries_.push(data[k].num_data[this.index].team_data[l].team_num);
                                    series_.data.push(eachSeries_);
                                }
                                seriesChart15.push(series_);
                            }
                            draw_chart15(seriesChart15);
                            draw_chart14(seriesChart15[1]);
                        }
                    }
                }
            }
        },
        series: chart13SeriesData

    });
    //返回总人力
    $("#off_chart_container").click(function () {
        if (authority == "admin") {
            $("#unitssetting").css("display", "block");
        } else {
            $("#unitssetting").css("display", "none");
        }
        // draw_chart13(data, authority);
        $("#unitspower_column_chart").css("display", "block");
        $("#chart_dron_down").css("display", "none");
    });
};

// UnitsPower 每个leader下的各个team的详细编制人力 饼状图
function draw_chart14(series_) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    $("#unitspower_pie_chart").highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            backgroundColor: "rgba(0,0,0,0)"
        },
        title: {
            text: series_.name + " 人力分布"
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: series_.name + " 人力分布",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        tooltip: {
            headerFormat: "{series.name}<br>",
            pointFormat: "{point.name}: <b>{point.percentage:.1f}%</b>"
        },
        credits: {
            enabled: false
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: "pointer",
                dataLabels: {
                    enabled: true,
                    format: "<b>{point.name}</b>: {point.y}<br>{point.name}: {point.percentage:.1f}%",
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || "black"
                    }
                }
            }
        },
        series: [{
            type: "pie",
            name: series_.name,
            data: series_.data
        }]
    });
};

// UnitsPower 每个leader下的各个team的详细编制人力 柱状图
function draw_chart15(seriesChart15) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    $("#unitspower_division_column").highcharts({
        chart: {
            type: "column",
            backgroundColor: "rgba(0,0,0,0)"
        },
        title: {
            text: "部门编制人力"
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "部门编制人力",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        xAxis: {
            type: "category"
        },
        credits: {
            enabled: false
        },
        plotOptions: {
            column: {
                borderWidth: 0,
                dataLabels: {
                    enabled: true,
                    crop: false,
                    overflow: "none",
                    format: "{point.y}",
                }
            },
            series: {
                cursor: "pointer",
                events: {
                    click: function (event) {
                        var index = event.point.series.index;
                        draw_chart14(seriesChart15[index]);
                    }
                }
            }
        },
        tooltip: {
            enabled: false
        },
        series: seriesChart15

    });
};

// 招募状况页面的 每个team当前的详细的招募状况
function draw_chart17(seriesData, x_categories, detailDataDict) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    var thisYearValue = new Date().getFullYear();
    $("#recruit_column_chart").highcharts({
        chart: {
            type: "column",
            backgroundColor: "rgba(0,0,0,0)"
        },
        // 下面数组里的颜色是该表格的树状图的颜色，按顺序一一对应
        colors: ["#058DC7", "#50B432", "#ED561B", "#DDDF00"],
        title: {
            text: thisYearValue + " 大陸師幹招募状况",
            useHTML: true,
            style: {
                // fontSize: "20px",
                fontSize: "2rem",
                color: "#333"
            }
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: thisYearValue + "-General-recruitment-of-mainland-divisions-01",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        xAxis: {
            categories: x_categories,
            labels: {

                style: {
                    // fontSize: '2rem',
                    color: "#333",
                    textOverflow: "clip",
                    textAlign: "center",
                },
                // useHTML: true,
                formatter: function () {
                    var x_value_list = this.value.split("&");
                    if (x_value_list.length >= 2) {
                        return x_value_list[0]
                    } else {
                        return x_value_list
                    }
                }
            },
            crosshair: true,
        },
        yAxis: {
            min: 0,
            title: {
                text: "人数(人)",
                style: {
                    fontSize: 16,
                    color: "#333"
                }
            },
            labels: {
                style: {
                    //fontSize: 14,
                    color: "#333",
                },
                useHTML: true,
            }
        },
        legend: {
            itemStyle: {
                "fontSize": "16px"
            }
        },
        credits: {
            enabled: false
        },
        tooltip: {
            enabled: false,
            headerFormat: "<span style=\"font-size:10px\">{point.key}</span><table>",
            pointFormat: "<tr><td style=\"color:{series.color};padding:0\">{series.name}: </td>" +
            "<td style=\"padding:0\"><b>{point.y} 人</b></td></tr>",
            footerFormat: "</table>",
            shared: true,
            useHTML: true
        },
        plotOptions: {
            column: {
                borderWidth: 0,
                cursor: "pointer",
                dataLabels: {
                    allowOverlap: true,
                    enabled: true,

                    crop:false,
                    overflow:'none',
                    style: {
                         // visibility: "visible",

                         opacity: "1",

                    }
                },
                cursor: "pointer",
                point: {
                    events: {
                        click: function () {
                            $("#demand_tab").html("");
                            $("#recruit_tab").html("");
                            $("#power_ly").modal();
                            var this_table_data = detailDataDict[this.category];
                            // console.log('this_table_data__',this_table_data);
                            for (var i = 0; i < this_table_data.length; i++) {
                                var demand_data = this_table_data[i][0];
                                var recruit_data = this_table_data[i][1];
                                getTbody(demand_data, "#" + "demand_tab");
                                for (var k = 0; k < recruit_data.length; k++) {
                                    getTbody(recruit_data[k], "#" + "recruit_tab");
                                }

                            }
                        }
                    }
                }
            },
        },
        series: seriesData
    });
}

//招募状况页面的 大陆师干总招募状况 柱形图
function draw_chart5(chart5SeriesData) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    var thisYearValue = new Date().getFullYear();
    $("#recruit_column_total").highcharts({
        chart: {
            type: "column",
            backgroundColor: "rgba(0,0,0,0)"
        },
        title: {
            text: thisYearValue + " 大陸師幹總招募状况",
            useHTML: true,
            style: {
                fontSize: "20px",
                color: "#333",
            }
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: thisYearValue + "-General-recruitment-of-mainland-divisions-02",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        legend: {
            enabled: false
        },
        xAxis: {
            categories: [
                "總需求人數",
                "總錄用已報到人數",
                "總錄用未報到人數",
                "總剩余需求",
            ],
            crosshair: true,
            labels: {
                useHTML: true,
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: "人数(人)"
            },
            labels: {
                useHTML: true,
            }
        },
        credits: {
            enabled: false
        },
        tooltip: {
            enabled: false,
            headerFormat: "<span style=\"font-size:10px\">{point.key}</span><table>",
            pointFormat: "<tr><td style=\"color:{series.color};padding:0\">{series.name}: </td>" +
            "<td style=\"padding:0\"><b>{point.y}</b></td></tr>",
            footerFormat: "</table>",
            shared: true,
            useHTML: true
        },
        plotOptions: {
            column: {
                borderWidth: 0,
                dataLabels: {
                    enabled: true,
                    style: {
                        fontWeight: "bold",
                        fontSize: "11px",
                        color: "#003399"
                    }
                }
            }
        },
        series: [{
            name: "",
            data: chart5SeriesData
        }]
    });
};

//招募状况页面的 每个team当前人力状况
function draw_chart6(teamName, chart6SeriesData) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    $("#recruit_column_manpower").highcharts({
        chart: {
            type: "column",
            backgroundColor: "rgba(0,0,0,0)"
        },
        title: {
            text: "人力状况",
            useHTML: true,
            style: {
                fontSize: "20px",
                color: "#333",
            }
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "The-human-condition-03",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        xAxis: {
            categories: teamName,
            labels: {
                //useHTML: true,
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: "人数(人)"
            },
            stackLabels: {
                enabled: true,
            },
            labels: {
                useHTML: true,
            }
        },
        tooltip: {
            enabled: false
        },
        plotOptions: {
            column: {
                // stacking: 'normal',
                dataLabels: {
                    enabled: true,
                    // color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white',
                    style: {
                        fontWeight: "bold",
                        fontSize: "11px",
                        color: "#003399"
                    }
                }
            }
        },
        credits: {
            enabled: false
        },
        series: chart6SeriesData

    });
};

// 离职页面的 按照日期show出 EERF师级离职率
function draw_chart8(chart8SeriesData, dimissionData) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart画图所需的参数
     */
    Highcharts.setOptions({
        lang: {
            shortMonths: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
    });

    $("#dimission_line_chart").highcharts("StockChart", {
        navigator:{
            xAxis: {
                labels: {
                    useHTML: true,

                }
            },
        },

        rangeSelector: {
            allButtonsEnabled: true,
            buttons: [

                {
                    type: "month",
                    count: 6,
                    text: "6m"
                },
                {
                    type: "year",
                    count: 1,
                    text: "1y"
                },
                {
                    type: "all",
                    text: "All"
                }
            ],
            selected: 1
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "EERF 师级离职率",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        xAxis: {
            type: "datetime",
            dateTimeLabelFormats: {
                day: "%Y<br/>%m-%d",
                month: "%Y-%m",
                year: "%Y"
            },
            labels: {
                useHTML: true,
            }
        },
        yAxis: {
            labels: {
                formatter: function () {
                    return this.value + "%";
                },
                useHTML: true,
            },
            title: {
                text: "离职状况分布"
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true,
                    crop: false,
                    overflow: "none",
                    format: "{point.y:.2f}%",
                }
            },
            series: {
                showInLegend: true,
                events: {
                    click: function (event) {
                        var thisPointData = dimissionData[event.point.index];
                        if (thisPointData.length == 0) {
                            ale();
                        } else {
                            var thisTeamNameList = [], thisMonthTeamData = [], thisMonthSeries = [],
                                thisMonthSpecific = [];
                            for (var i = 0; i < thisPointData.length; i++) {
                                thisTeamNameList.push(thisPointData[i].name);
                                thisMonthSeries.push(thisPointData[i].num);
                                thisMonthTeamData.push(thisPointData[i].zong);
                                thisMonthSpecific.push(thisPointData[i].speific_info);
                            }
                            for (var i = 0; i < thisMonthTeamData.length; i++) {
                                thisMonthTeamData[i] = parseInt(thisMonthTeamData[i] * 100) / 100;
                            }
                            $("#dissmision_off_chart").css("display", "block");
                            // alert(this.chart.hoverPoint.key);
                            // 处理点击选择的日期
                            month_array = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06', 'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'};
                            month_key = this.chart.hoverPoint.key.split(" ")[0];
                            month_data = month_array[month_key];
                            year_key = this.chart.hoverPoint.key.split(" ")[1];
                            draw_chart7_mouse(thisTeamNameList, thisMonthTeamData, thisMonthSpecific, thisMonthSeries, month_data, year_key);
                            $("#dissmision_off_chart").click(function () {
                                draw_chart7(team_name_list, team_data_list, specific_info, team_leave_num);
                                $(this).css("display", "none");
                            });
                        }
                    }
                }
            }
        },
        chart: {
            backgroundColor: "rgba(0,0,0,0)"
        },
        title: {
            text: "EERF 师级离职率",
            useHTML: true,
            style: {
                fontSize: "18px",
            }
        },
        tooltip: {
            split: false,
            shared: false,
            valueDecimals: 2,
            dateTimeLabelFormats: {
                month: "%B %Y",
                year: "%Y"
            },
            pointFormatter: function () {
                function getdate(x) {
                    var date = new Date(x);
                    var y = date.getFullYear();
                    var m = "-" + (date.getMonth() + 1 < 10 ? "0" + (date.getMonth() + 1) : date.getMonth() + 1);
                    var d = "-" + date.getDate();
                    return y + m + d;
                }

                return getdate(this.x) + "<br><span style=\"color: " + this.series.color + "\"></span> " +
                    this.series.name + ": <b>" + this.y + "%" + "</b>.";
            }
        },

        credits: {
            enabled: false
        },
        series: [{
            name: "离职率",
            data: chart8SeriesData,
        }]

    });

};

// 画出离职状况页面的 师级离职状况 柱形图，并show出每个leader下离职的人的信息
function draw_chart7(team_name_list, team_data_list, specific_info, team_leave_num) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    var date = new Date();
    // console.log("aaaaa",teamDataList);
    var y = date.getFullYear();
    $("#dimission_column_chart").highcharts({
        chart: {
            type: "column",
            backgroundColor: "rgba(0,0,0,0)"
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: y + " 师级实时离职状况",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        title: {
            text: y + " 师级实时离职状况",
            useHTML: true,
        },
        xAxis: {
            categories: team_name_list,
            labels: {
                // useHTML: true,
            }
        },
        yAxis: {
            // min: 0,
            // minRange: 18,
            title: {
                text: "百分比"
            },
            labels: {
                useHTML: true,
            }
        },
        credits: {
            enabled: false
        },
        series: [{
            name: "人力离职状况分布",
            data: team_data_list
        }],
        tooltip: {
            enabled: true,
            formatter: function () {
                // console.log('this',this);
                return "离职的人数: <b>" + team_leave_num[this.point.index] + "</b>";
            }
        },
        plotOptions: {
            column: {
                borderWidth: 0,
                dataLabels: {
                    format: "{y}%",
                    enabled: true,
                    style: {
                        fontWeight: "bold",
                        fontSize: "11px",
                        color: "#003399"
                    }
                },
                cursor: "pointer",
                point: {
                    events: {
                        click: function (event) {
                            createTbody("specific_dimission_tab");
                            var index = event.point.index;
                            var data = specific_info[index];
                            for (var i = 0; i < data.length; i++) {
                                $("#specific_dimission_tab").append("<tr><td>" + data[i].id + "</td><td>" + data[i].name + "</td><td>" + data[i].grade + "</td><td>" + data[i].difference + "</td><td>" + data[i].seniority + "</td><td>" + data[i].team + "</td><td>" + data[i].leave_date + "</td></tr>");
                            }
                            $("#dimission_ly").modal();

                        }
                    }
                },
            }
        }
    });
};
/************************************************************************************************************************/
// 画出离职状况页面的 师级离职状况 柱形图，并show出每个leader下离职的人的信息
function draw_chart7_mouse(team_name_list, team_data_list, specific_info, team_leave_num, month_data, year_key) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    var date = new Date();
    // console.log("aaaaa",teamDataList);
    var y = date.getFullYear();
    $("#dimission_column_chart").highcharts({
        chart: {
            type: "column",
            backgroundColor: "rgba(0,0,0,0)"
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: y + " 师级实时离职状况",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        title: {
            text: year_key + "-" + month_data + " 师级实时离职状况",
            useHTML: true,
        },
        xAxis: {
            categories: team_name_list,
            labels: {
                useHTML: true,
            }
        },
        yAxis: {
            // min: 0,
            // minRange: 18,
            title: {
                text: "百分比"
            },
            labels: {
                useHTML: true,
            }
        },
        credits: {
            enabled: false
        },
        series: [{
            name: "人力离职状况分布",
            data: team_data_list
        }],
        tooltip: {
            enabled: true,
            formatter: function () {
                // console.log('this',this);
                return "离职的人数: <b>" + team_leave_num[this.point.index] + "</b>";
            }
        },
        plotOptions: {
            column: {
                borderWidth: 0,
                dataLabels: {
                    format: "{y}%",
                    enabled: true,
                    style: {
                        fontWeight: "bold",
                        fontSize: "11px",
                        color: "#003399"
                    }
                },
                cursor: "pointer",
                point: {
                    events: {
                        click: function (event) {
                            createTbody("specific_dimission_tab");
                            var index = event.point.index;
                            var data = specific_info[index];
                            for (var i = 0; i < data.length; i++) {
                                $("#specific_dimission_tab").append("<tr><td>" + data[i].id + "</td><td>" + data[i].name + "</td><td>" + data[i].grade + "</td><td>" + data[i].difference + "</td><td>" + data[i].seniority + "</td><td>" + data[i].team + "</td><td>" + data[i].leave_date + "</td></tr>");
                            }
                            $("#dimission_ly").modal();

                        }
                    }
                },
            }
        }
    });
};

/************************************************************************************************************************/
// 离职原因分析 饼状图
function draw_chart19(chart19SeriesData, chart19DrilldownSeries) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    $("#dimission_pie_chart").highcharts({
        chart: {
            type: "pie",
            backgroundColor: "rgba(0,0,0,0)"
        },
        title: {
            text: "离职原因分析",
            useHTML: true,
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "离职原因分析",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        plotOptions: {
            series: {
                dataLabels: {
                    enabled: true,
                    format: "<b>{point.name}</b>:{point.percentage:.1f}%",
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || "black"
                    }
                },
                point: {
                    events: {
                        click: function (event) {
                            $("#dissmision_off_chart_2").css("display", "none");
                            $("#dissmision_off_chart_3").css("display", "block");
                        }
                    }
                },
            }
        },
        tooltip: {
            headerFormat: "<span style=\"font-size:11px\">{series.name}</span><br>",
            pointFormat: "<span style=\"color:{point.color}\">{point.name}</span>: <b>{point.percentage:.1f}%</b><br/>"
        },
        series: [{
            name: "离职原因占比",
            colorByPoint: true,
            data: chart19SeriesData
        }],
        drilldown: {
            drillUpButton: {
                relativeTo: "spacingBox",
                position: {
                    y: 0,
                    x: 10000
                },
                theme: {
                    fill: "white",
                    "stroke-width": 1,
                    stroke: "silver",
                    r: 0,
                    states: {
                        hover: {
                            fill: "#bada55"
                        },
                        select: {
                            stroke: "#039",
                            fill: "#bada55"
                        }
                    }
                }
            },
            series: chart19DrilldownSeries
        }
    });
}

/**
 * 考勤加班模块 4个页面
 * overtimework： Overtimework_column_chart(),draw_chart11()
 * overwork： draw_chart16(),draw_chart12()
 * nightwork: Nightwork_column_chart(),draw_chart9(),
 * eveningtrips: Eveningtrips_column_chart(),draw_chart10()
 */

// $("input[type='checkbox']").prop("checked", false);
// 按照日期 每月的整个EERF的超時加班時數的柱状图
function Overtimework_column_chart(dataList, draw_chart11_series_data, draw_chart11_section_data) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    Overtimework_Datas = dataList;
    Overtimework_Series = draw_chart11_series_data;
    // 全局配置，对当前页面的所有图表有效
    Highcharts.setOptions({
        lang: {
            // 月份
            shortMonths: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
    });

    Highcharts.stockChart("overtimework_column_chart", {
        rangeSelector: {
            allButtonsEnabled: true,
            buttons: [
                {
                    type: "month",
                    count: 6,
                    text: "6m"
                },
                {
                    type: "year",
                    count: 1,
                    text: "1y"
                },
                {
                    type: "all",
                    text: "All"
                }
            ],
            selected: 1
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "超時加班時數",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        title: {
            text: "超時加班時數",
            style: {
                fontSize: "20px",
            }
        },
        xAxis: {
            type: "datetime",
            dateTimeLabelFormats: {
                day: "%Y<br/>%m-%d",
                month: "%Y-%m",
                year: "%Y"
            }
        },
        yAxis: {
            title: {
                text: "時數(h)"
            }
        },
        tooltip: {
            xDateFormat: "%B %Y" + "<br/>" + "%Y-%m-%d",
        },
        plotOptions: {
            column: {
                dataLabels: {
                    enabled: true,
                    crop: false,
                    overflow: "none",
                    format: "{point.y:2f}",
                },
                point: {
                    events: {
                        click: function () {
                            var thisYearTimestamp = new Date("2018-01-1 00:00:00").getTime();
                            if (this.x >= thisYearTimestamp) {
                                $("#search_chart_contain").css("display", "block");
                                $("#overtimework_column_chart").css("display", "none");
                                $("#section_search_chart_contain").css("display", "none");
                                $("#check_div").empty();
                                $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
                                $("#check_div_copy").empty();
                                $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");

                                draw_chart11(draw_chart11_series_data, draw_chart11_section_data);
                            }
                            else {
                                alert("该节点没有数据");
                            }
                        }
                    }
                }
            },
            series: {
                showInLegend: true
            }
        },
        chart: {
            backgroundColor: "rgba(0,0,0,0)"
        },
        credits: {
            enabled: false
        },
        series: dataList
    });
    // 点击后退按钮对应的函数(考勤第二层后退到第一层)
    $("#off_search_chart_contain").click(function () {
        /* 重新畫圖，避免下載圖后空白 */
        if ($("#overtimework_column_chart").css("display") === 'none') {
            $("#search_chart_contain").css("display", "none");
            $("#overtimework_column_chart").css("display", "block");
            $("#overtimework_column_chart").empty();
            $("#check_div").empty();
            $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
            $("#check_div_copy").empty();
            $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");

            for (var i=0; i< draw_chart11_series_data.length; i++) {
                draw_chart11_series_data[i].visible = true;
            }
            Overtimework_column_chart(Overtimework_Datas, Overtimework_Series, draw_chart11_section_data);
        }
    });
}

function show_overtimework_modal(attendanceInfo, series_name, this_date, this_color) {
    createTbody("specific_overtimework_tab");
    $("#Time").html(this_date);
    $("#Leader").html(series_name);
    $("#overtimework_caption").css("backgroundColor", this_color);
    $("#specific_overtimework_tab").css("borderColor", this_color);
    for (var i = 0; i < attendanceInfo.length; i++) {
        $("#specific_overtimework_tab").append("<tr><td>" + attendanceInfo[i].a_employee + "</td><td>" + attendanceInfo[i].a_name + "</td><td>" +
            parseFloat(attendanceInfo[i].a_totaldutyhours).toFixed(2) + "</td><td>" + parseFloat(attendanceInfo[i].a_avgdutyhours).toFixed(2) + "</td><td>" + parseFloat(attendanceInfo[i].a_maxdutyhours).toFixed(2) + "</td><td>" +
            attendanceInfo[i].a_dutydays + "</td><td>" + parseFloat(attendanceInfo[i].a_totalhours).toFixed(2) + "</td><td>" + attendanceInfo[i].a_totaldays +
            "</td><td>" + parseFloat(attendanceInfo[i].a_avghours).toFixed(2) + "</td><td>" + parseFloat(attendanceInfo[i].a_maxhours).toFixed(2) + "</td></tr>");
    }
}

function click_overtimework_th(all_attendanceInfo,series_name, this_date, this_color) {
    $(".nightwork_th_bac").click(function () {
        // console.log('this click name:',this,$(this).attr('name'));
        var the_key = $(this).attr('name');

        show_overtimework_modal(all_attendanceInfo[the_key],series_name, this_date, this_color)
    })
}

// 按照日期 每月的每个leader下的超时加班时数
function draw_chart11(seriesData, sectionData) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    seriesData_data = seriesData;
    Highcharts.setOptions({
        lang: {
            shortMonths: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
    });

    $("input[type='checkbox']").prop("checked", false);
    $("#overtimework_line_chart").highcharts("StockChart", {
        rangeSelector: {
            allButtonsEnabled: true,
            buttons: [
                {
                    type: "month",
                    count: 6,
                    text: "6m"
                },
                {
                    type: "year",
                    count: 1,
                    text: "1y"
                },
                {
                    type: "all",
                    text: "All"
                }
            ],
            selected: 1
        },
        colors: ["#CC99CC", "#99CC99", "#669999", "#009966", "#CC6600", "#CCCC33", "#336699", "#FF6666", "#999999", "#009933"],
        chart: {
            backgroundColor: "rgba(0,0,0,0)",
            zoomType: "xy",
            style: {
                fontSize: "18px"
            }
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "超時加班時數",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600,
        },
        title: {
            text: "超時加班時數",
            style: {
                fontSize: "20px",
            }
        },
        credits: {
            enabled: false
        },
        legend: {
            enabled: true
        },
        xAxis: {
            type: "datetime",
            dateTimeLabelFormats: {
                day: "%Y<br/>%m-%d",
                month: "%Y-%m",
                year: "%Y"
            },
            // crosshair: {
            //     width: 3,
            //     color: 'green',
            //     snap:false
            // }
        },
        yAxis: {
            labels: {
                formatter: function () {
                    return this.value;
                }
            },
            title: {
                text: "时数(h)"
            },
            // crosshair: {
            //     width: 3,
            //     color: 'green',
            //     snap:false
            // }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true,
                    crop: false,
                    // allowOverlap:true
                    //overflow: 'none',
                    //format:'{point.y:.2f}%',
                },
                point: {
                    events: {
                        click: function () {
                            var thisYearTimestamp = new Date("2018-01-1 00:00:00").getTime();
                            if (this.x >= thisYearTimestamp) {
                                $("#search_chart_contain").css("display", "none");
                                $("#overtimework_column_chart").css("display", "none");
                                $("#section_search_chart_contain").css("display", "block");
                                $("#check_div").empty();
                                $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
                                $("#check_div_copy").empty();
                                $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
                                // 科级数据筛选
                                var all_attendanceInfo = getAttendanceInfo(this.x, this.colorIndex);
                                leader_name = this.series.userOptions.name;
                                b = all_attendanceInfo[1];
                                sectionData_list = [];
                                for (i in all_attendanceInfo){
                                    d = all_attendanceInfo[i];
                                    for (j in sectionData)
                                        if (d == sectionData[j].name){
                                            sectionData_list.push(sectionData[j]);
                                            break
                                        }
                                }
                                draw_chart11_next(sectionData_list, leader_name);
                            }
                            else {
                                alert("该节点没有数据");
                            }

                        }
                    }
                },
            },
            series: {
                cursor: "pointer",
                showInLegend: true,
                // allowPointSelect: true,
                marker: {
                    radius: 10
                },
                states: {
                    hover: {
                        lineWidthPlus: 15
                    }
                }
            }
        },
        tooltip: {
            split: false,
            shared: false,
            xDateFormat: "<br/>" + "%Y-%m-%d",
            style: {
                fontSize: "15px"
            }
        },
        series: seriesData
    },function (c) {
        checklegend(c);
    });
    // 点击后退按钮对应的函数(考勤第三层后退到第二层)
    $("#off_search_chart_contain_section").click(function () {
        setTimeout(function () {
            /* 重新畫圖，避免下載圖后空白 */
            if ($("#search_chart_contain").css("display") === 'none') {
                $("#section_search_chart_contain").css("display", "none");
                $("#search_chart_contain").css("display", "block");
                $("#overtimework_line_chart").empty();
                $("#check_div").empty();
                $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
                $("#check_div_copy").empty();
                $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");

                // for (var i=0; i< seriesData.length; i++) {
                //     seriesData[i].visible = true;
                // }
                draw_chart11(seriesData_data, sectionData);
            }

        }, 600)
    });

}

/**************************************************************************************************************************/
// 按照日期 leader下的对应科级超时加班时数
function draw_chart11_next(seriesData, leader_name) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    Highcharts.setOptions({
        lang: {
            shortMonths: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
    });

    $("input[type='checkbox']").prop("checked", false);
    $("#section_overtimework_line_chart").highcharts("StockChart", {
        rangeSelector: {
            allButtonsEnabled: true,
            buttons: [
                {
                    type: "month",
                    count: 6,
                    text: "6m"
                },
                {
                    type: "year",
                    count: 1,
                    text: "1y"
                },
                {
                    type: "all",
                    text: "All"
                }
            ],
            selected: 1
        },
        colors: ["#CC99CC", "#99CC99", "#669999", "#009966", "#CC6600", "#CCCC33", "#336699", "#FF6666", "#999999", "#009933"],
        chart: {
            backgroundColor: "rgba(0,0,0,0)",
            zoomType: "xy",
            style: {
                fontSize: "18px"
            }
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename:"【" + leader_name +  "】 " + "team超時加班時數",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        title: {
            text: "【" + leader_name +  "】 " + "team超時加班時數",
            style: {
                fontSize: "20px",
            }
        },
        credits: {
            enabled: false
        },
        legend: {
            enabled: true
        },
        xAxis: {
            type: "datetime",
            dateTimeLabelFormats: {
                day: "%Y<br/>%m-%d",
                month: "%Y-%m",
                year: "%Y"
            },
            // crosshair: {
            //     width: 3,
            //     color: 'green',
            //     snap:false
            // }
        },
        yAxis: {
            labels: {
                formatter: function () {
                    return this.value;
                }
            },
            title: {
                text: "时数(h)"
            },
            // crosshair: {
            //     width: 3,
            //     color: 'green',
            //     snap:false
            // }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true,
                    crop: false,
                    // allowOverlap:true
                    //overflow: 'none',
                    //format:'{point.y:.2f}%',
                },
                point: {
                    events: {
                        click: function () {
                            $('.nightwork_th_bac').css("background-color",'rgba(0, 0, 0, 0)');
                            $('.nightwork_th_bac').css("font-size",'1.6rem');
                            $('.nightwork_th_bac').eq(1).css("background-color",'rgb(222, 146, 141)');

                            var thisYearTimestamp = new Date("2018-05-1 00:00:00").getTime();
                            if (this.x >= thisYearTimestamp) {
                                var all_attendanceInfo = getAttendanceInfoFour(this.x, this.colorIndex);
                                $("#overtimework_modal").modal();
                                show_overtimework_modal(all_attendanceInfo['a_avgdutyhours'],this.series.name,this.key.slice(5),this.color);
                                click_overtimework_th(all_attendanceInfo,this.series.name,this.key.slice(5),this.color);
                            }
                            else {
                                alert("该节点没有数据");
                            }
                        }
                    }
                },
            },
            series: {
                cursor: "pointer",
                showInLegend: true,
                // allowPointSelect: true,
                marker: {
                    radius: 10
                },
                states: {
                    hover: {
                        lineWidthPlus: 15
                    }
                }
            }
        },
        tooltip: {
            split: false,
            shared: false,
            xDateFormat: "<br/>" + "%Y-%m-%d",
            style: {
                fontSize: "15px"
            }
        },
        series: seriesData
    },function (c) {
        checklegend(c);
    });
   $('.nightwork_th_bac').click(function(){
        if ($(this).css("background-color") === 'rgba(0, 0, 0, 0)') {
             $('.nightwork_th_bac').css("background-color",'rgba(0, 0, 0, 0)')
             $('.nightwork_th_bac').css("font-size",'1.6rem')
             $(this).css("background-color",'rgb(222, 146, 141)')
             $(this).css("font-size",'18px')
             $(this).css("box-shadow",'0px 0px 7px 2px #332e2e inset')
        }
    })
}
/**************************************************************************************************************************/

// checkbox 事件 全选or全不选
function checklegend(chart) {
    $(".check_legend").click(function () {
        var self = $(this);
        var checked = self.prop('checked');
        if(checked) {
            for (let i = 0; i < chart.series.length; i++) {
                chart.series[i].hide();
            }
        }else {
            for (let j = 0; j < chart.series.length; j++) {
                chart.series[j].show();
            }
        }
    });

    /* 修改 checkbox 的状态 */
    $(".highcharts-legend").click(function () {
        var checkedFlag = chart.series.length;
        for (let k = 0; k < chart.series.length; k++) {
            if (chart.series[k].visible) {
                checkedFlag += 1;
            } else {
                checkedFlag -= 1;
            }
        }
        if (checkedFlag === 0) {
            $("input[type='checkbox']").prop("checked", true);
        } else {
            $("input[type='checkbox']").prop("checked", false);
        }
    });
}

// 每月 EERF的工作超时（超时加班9,9.5,10,10.5,11小时） 的人数
function draw_chart16(dataList, chart12_data_list, chart_title, chart12_section_data_list) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    drawChart16Datas = dataList;
    drawChart16Title = chart_title;
    chart12_data_listTitle = chart12_data_list;
    Highcharts.setOptions({
        lang: {
            shortMonths: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
    });

    Highcharts.stockChart("overwork_column_chart", {
        rangeSelector: {
            allButtonsEnabled: true,
            buttons: [
                {
                    type: "month",
                    count: 6,
                    text: "6m"
                },
                {
                    type: "year",
                    count: 1,
                    text: "1y"
                },
                {
                    type: "all",
                    text: "All"
                }
            ],
            selected: 1
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "工作超時人數",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        title: {
            text: chart_title,
            style: {
                fontSize: "20px",
            }
        },
        xAxis: {
            type: "datetime",
            dateTimeLabelFormats: {
                day: "%Y<br/>%m-%d",
                month: "%Y-%m",
                year: "%Y"
            }
        },
        yAxis: {
            title: {
                text: "人数(人)"
            }
        },
        tooltip: {
            xDateFormat: "%B %Y" + "<br/>" + "%Y-%m-%d",
        },
        plotOptions: {
            column: {
                dataLabels: {
                    enabled: true,
                    crop: false,
                    overflow: "none",
                    format: "{point.y:2f}",
                },
                point: {
                    events: {
                        click: function () {
                            var thisYearTimestamp = new Date("2018-01-1 00:00:00").getTime();
                            if (this.x >= thisYearTimestamp) {
                                $("#search_chart_contain").css("display", "block");
                                $("#overwork_column_chart").css("display", "none");
                                $("#section_search_chart_contain").css("display", "none");
                                $("#check_div").empty();
                                $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
                                $("#check_div_copy").empty();
                                $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");

                                draw_chart12(chart12_data_list, chart_title, chart12_section_data_list);
                                $("#search_con2").css("display", "none");
                            }
                            else {
                                alert("该节点没有数据");
                            }
                        }
                    }
                }
            },
            series: {
                showInLegend: true
            }
        },
        chart: {
            backgroundColor: "rgba(0,0,0,0)"
        },
        credits: {
            enabled: false
        },
        series: dataList
    });
    // 点击后退按钮对应的函数(考勤第二层后退到第一层)
    $("#off_search_chart_contain").click(function () {
        // draw_chart16(dataList, chart12_data_list);
        /* 重新畫圖，避免下載圖后空白 */
        if ($("#overwork_column_chart").css("display") === 'none') {
            $("#search_chart_contain").css("display", "none");
            $("#overwork_column_chart").css("display", "block");
            $("#overwork_column_chart").empty();
            $("#check_div").empty();
            $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
            $("#check_div_copy").empty();
            $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");

            draw_chart16(drawChart16Datas, chart12_data_listTitle, drawChart16Title, chart12_section_data_list);
            for (var i=0; i< chart12_data_list.length; i++) {
                chart12_data_list[i].visible = true;
            }
            $("#search_con2").css("display", "block");
        }
    });

}

function show_overwork_modal(attendanceInfo, series_name, this_date, this_color) {
    createTbody("specific_overwork_tab");
    $("#Leader").html(series_name);
    $("#Time").html(this_date);
    $("#overwork_caption").css("backgroundColor", this_color);
    $("#specific_overwork_tab").css("borderColor", this_color);
    for (var i = 0; i < attendanceInfo.length; i++) {
        $("#specific_overwork_tab").append("<tr><td>" + attendanceInfo[i].a_employee + "</td><td>" + attendanceInfo[i].a_name + "</td><td>" +
            parseFloat(attendanceInfo[i].a_totaloverhours).toFixed(2) + "</td><td>" + parseFloat(attendanceInfo[i].a_avgoverhours).toFixed(2) + "</td><td>" + parseFloat(attendanceInfo[i].a_maxoverhours).toFixed(2) + "</td><td>" +
            parseFloat(attendanceInfo[i].a_totalhours).toFixed(2) + "</td><td>" + attendanceInfo[i].a_totaldays +
            "</td><td>" + parseFloat(attendanceInfo[i].a_avghours).toFixed(2) + "</td><td>" + parseFloat(attendanceInfo[i].a_maxhours).toFixed(2) + "</td></tr>");
    }
}

function click_overwork_th(all_attendanceInfo,series_name, this_date, this_color) {
    $(".nightwork_th_bac").click(function () {
        // console.log('this click name:',this,$(this).attr('name'));
        var the_key = $(this).attr('name');

        show_overwork_modal(all_attendanceInfo[the_key],series_name, this_date, this_color)
    })
}

// 每月每个leader下工作超时（超时加班9,9.5,10,10.5,11小时）的人数
function draw_chart12(seriesData, chart_title, sectionData) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    seriesData_data = seriesData;
    Highcharts.setOptions({
        lang: {
            shortMonths: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
    });

    $("input[type='checkbox']").prop("checked", false);
    $("#overwork_line_chart").highcharts("StockChart", {
        rangeSelector: {
            allButtonsEnabled: true,
            buttons: [
                {
                    type: "month",
                    count: 6,
                    text: "6m"
                },
                {
                    type: "year",
                    count: 1,
                    text: "1y"
                },
                {
                    type: "all",
                    text: "All"
                }
            ],
            selected: 1
        },
        colors: ["#CC99CC", "#99CC99", "#669999", "#009966", "#CC6600", "#CCCC33", "#336699", "#FF6666", "#999999", "#009933"],
        chart: {
            backgroundColor: "rgba(0,0,0,0)",
            zoomType: "xy",
            style: {
                fontSize: "18px"
            }
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "工作超時人數",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        title: {
            text: chart_title,
            style: {
                fontSize: "20px",
            }
        },
        credits: {
            enabled: false
        },
        legend: {
            enabled: true
        },
        xAxis: {
            type: "datetime",
            dateTimeLabelFormats: {
                day: "%Y<br/>%m-%d",
                month: "%Y-%m",
                year: "%Y"
            }
        },
        yAxis: {
            labels: {
                formatter: function () {
                    return this.value;
                }
            },
            title: {
                text: "人数(人)"
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true,
                    crop: false,
                    // allowOverlap:true
                    //overflow: 'none',
                    //format:'{point.y:.2f}%',
                },
                point: {
                    events: {
                        click: function () {
                            var thisYearTimestamp = new Date("2018-05-1 00:00:00").getTime();
                            if (this.x >= thisYearTimestamp) {
                                $("#search_chart_contain").css("display", "none");
                                $("#overwork_column_chart").css("display", "none");
                                $("#section_search_chart_contain").css("display", "block");
                                $("#check_div").empty();
                                $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
                                $("#check_div_copy").empty();
                                $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");

                                var all_attendanceInfo = getAttendanceInfo(this.x, this.colorIndex);
                                leader_name = this.series.userOptions.name;
                                b = all_attendanceInfo[1];
                                sectionData_list = [];
                                for (i in all_attendanceInfo){
                                    d = all_attendanceInfo[i];
                                    for (j in sectionData)
                                        if (d == sectionData[j].name){
                                            sectionData_list.push(sectionData[j]);
                                            break
                                        }
                                };
                                draw_chart12_next(sectionData_list, chart_title, leader_name);
                                $("#search_con2").css("display", "none");
                            }
                            else {
                                alert("该节点没有数据");
                            }
                        }
                    }
                }
            },
            series: {
                cursor: "pointer",
                showInLegend: true,
                // allowPointSelect: true,
                marker: {
                    radius: 10
                },
                states: {
                    hover: {
                        lineWidthPlus: 15
                    }
                }
            }
        },
        tooltip: {
            split: false,
            shared: false,
            xDateFormat: "<br/>" + "%Y-%m-%d",
            style: {
                fontSize: "15px"
            }
        },
        series: seriesData
    },function (c) {
        checklegend(c);
    });
    // 点击后退按钮对应的函数(考勤第三层后退到第二层)
     $("#off_search_chart_contain_section").click(function () {
        // draw_chart16(dataList, chart12_data_list);
          setTimeout(function () {
            /* 重新畫圖，避免下載圖后空白 */
            if ($("#search_chart_contain").css("display") === 'none') {
                $("#section_search_chart_contain").css("display", "none");
                $("#search_chart_contain").css("display", "block");
                $("#overwork_line_chart").empty();
                $("#check_div").empty();
                $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
                $("#check_div_copy").empty();
                $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");

                draw_chart12(seriesData_data, chart_title, sectionData);
            }
        }, 600)
    });
}

/****************************************************************************************************/
// 每月每个leader下工作超时（超时加班9,9.5,10,10.5,11小时）的人数
function draw_chart12_next(seriesData, chart_title, leader_name) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    chart_title = chart_title.split("EERF")[1];
    Highcharts.setOptions({
        lang: {
            shortMonths: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
    });

    $("input[type='checkbox']").prop("checked", false);
    $("#section_overwork_line_chart").highcharts("StockChart", {
        rangeSelector: {
            allButtonsEnabled: true,
            buttons: [
                {
                    type: "month",
                    count: 6,
                    text: "6m"
                },
                {
                    type: "year",
                    count: 1,
                    text: "1y"
                },
                {
                    type: "all",
                    text: "All"
                }
            ],
            selected: 1
        },
        colors: ["#CC99CC", "#99CC99", "#669999", "#009966", "#CC6600", "#CCCC33", "#336699", "#FF6666", "#999999", "#009933"],
        chart: {
            backgroundColor: "rgba(0,0,0,0)",
            zoomType: "xy",
            style: {
                fontSize: "18px"
            }
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "【" + leader_name +  "】 team" +"工作超時人數",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        title: {
            text: "【" + leader_name +  "】 team" + chart_title,
            style: {
                fontSize: "20px",
            }
        },
        credits: {
            enabled: false
        },
        legend: {
            enabled: true
        },
        xAxis: {
            type: "datetime",
            dateTimeLabelFormats: {
                day: "%Y<br/>%m-%d",
                month: "%Y-%m",
                year: "%Y"
            }
        },
        yAxis: {
            labels: {
                formatter: function () {
                    return this.value;
                }
            },
            title: {
                text: "人数(人)"
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true,
                    crop: false,
                    // allowOverlap:true
                    //overflow: 'none',
                    //format:'{point.y:.2f}%',
                },
                point: {
                    events: {
                        click: function () {
                            $('.nightwork_th_bac').css("background-color",'rgba(0, 0, 0, 0)')
                            $('.nightwork_th_bac').css("font-size",'1.6rem')
                            $('.nightwork_th_bac').eq(1).css("background-color",'rgb(222, 146, 141)')
                            var thisYearTimestamp = new Date("2018-05-1 00:00:00").getTime();
                            if (this.x >= thisYearTimestamp) {
                                var all_attendanceInfo = getAttendanceInfoFour(this.x, this.colorIndex);
                                $("#overwork_modal").modal();
                                show_overwork_modal(all_attendanceInfo['a_avgoverhours'],this.series.name,this.key.slice(5),this.color);
                                click_overwork_th(all_attendanceInfo,this.series.name,this.key.slice(5),this.color);
                            }
                            else {
                                alert("该节点没有数据");
                            }
                        }
                    }
                }
            },
            series: {
                cursor: "pointer",
                showInLegend: true,
                // allowPointSelect: true,
                marker: {
                    radius: 10
                },
                states: {
                    hover: {
                        lineWidthPlus: 15
                    }
                }
            }
        },
        tooltip: {
            split: false,
            shared: false,
            xDateFormat: "<br/>" + "%Y-%m-%d",
            style: {
                fontSize: "15px"
            }
        },
        series: seriesData
    },function (c) {
        checklegend(c);
    });
    $('.nightwork_th_bac').click(function(){
        if ($(this).css("background-color") === 'rgba(0, 0, 0, 0)') {
             $('.nightwork_th_bac').css("background-color",'rgba(0, 0, 0, 0)')
             $('.nightwork_th_bac').css("font-size",'1.6rem')
             $(this).css("background-color",'rgb(222, 146, 141)')
             $(this).css("font-size",'18px')
             $(this).css("box-shadow",'0px 0px 7px 2px #332e2e inset')
        }
    })
}
/****************************************************************************************************/

// 按照日期 每月整个EERF的晚点下班人次统计的柱状图
function Nightwork_column_chart(dataList, chart9SeriesData, chart9SectionData, yAxisTitle, chart_title) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    NightworkColumnChartDatas = dataList;
    NightworkColumnChartTitle = chart_title;
    NightworkChart9SeriesData = chart9SeriesData;
    NightworkChart9SectionData = chart9SectionData;
    NightworkYAxisTitle = yAxisTitle;
    Highcharts.setOptions({
        lang: {
            shortMonths: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
    });
    if (yAxisTitle === '人數(人)') {
        var yAxisTitle9 = '人次(人)';
        var plotOptionsValue = '';
    } else if (yAxisTitle === '天數(天)') {
        var yAxisTitle9 = '天數(天)';
        var plotOptionsValue = '';
    } else {
        var yAxisTitle9 = '百分比(%)';
        var plotOptionsValue = '%';
    }
    

    Highcharts.stockChart("nightwork_column_chart", {
        navigator:{
            xAxis: {
                labels: {
                    useHTML: true,

                }
            },
        },
        rangeSelector: {
            allButtonsEnabled: true,
            buttons: [
                {
                    type: "month",
                    count: 6,
                    text: "6m"
                },
                {
                    type: "year",
                    count: 1,
                    text: "1y"
                },
                {
                    type: "all",
                    text: "All"
                }
            ],
            selected: 1
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "晚點下班人數",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        title: {
            text: chart_title,
            useHTML: true,
            style: {
                fontSize: "20px",
            }
        },
        xAxis: {
            type: "datetime",
            dateTimeLabelFormats: {
                day: "%Y<br/>%m-%d",
                month: "%Y-%m",
                year: "%Y"
            },
            labels: {
                useHTML: true,
            }
        },
        yAxis: {
            title: {
                text: yAxisTitle
            },
            labels: {
                useHTML: true,

            }
        },
        tooltip: {
            xDateFormat: "%B %Y" + "<br/>" + "%Y-%m-%d",
        },
        plotOptions: {
            column: {
                dataLabels: {
                    enabled: true,
                    crop: false,
                    overflow: "none",
                    format: "{point.y:2f}" + plotOptionsValue,
                },
                point: {
                    events: {
                        click: function () {
                            $('.nightwork_th_bac').css("background-color",'rgba(0, 0, 0, 0)')
                            $('.nightwork_th_bac').css("font-size",'1.6rem')
                            $('.nightwork_th_bac').eq(1).css("background-color",'rgb(222, 146, 141)')
                            var thisYearTimestamp = new Date("2018-01-1 00:00:00").getTime();
                            if (this.x >= thisYearTimestamp) {
                                $("#search_chart_contain").css("display", "block");
                                $("#nightwork_column_chart").css("display", "none");
                                $("#section_search_chart_contain").css("display", "none");
                                $("#check_div").empty();
                                $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
                                $("#check_div_copy").empty();
                                $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");

                                draw_chart9(chart9SeriesData, chart9SectionData, yAxisTitle9, chart_title, plotOptionsValue);
                                $("#search_con1").css("display", "none");
                                $("#left_but").css("display","none");
                                $("#bagbtn").css("display","none");
                                $("#off_search_chart_contain").css("margin-top","0.5%");
                            }
                        }
                    }
                }
            },
            series: {
                showInLegend: true
            }
        },
        chart: {
            backgroundColor: "rgba(0,0,0,0)"
        },
        credits: {
            enabled: false
        },
        series: dataList
    });
    // 点击后退按钮对应的函数(考勤第二层后退到第一层)
    $("#off_search_chart_contain").click(function () {
        /* 重新畫圖，避免下載圖后空白 */
        if ($("#nightwork_column_chart").css("display") === 'none') {
            $("#search_chart_contain").css("display", "none");
            $("#nightwork_column_chart").css("display", "block");
            $("#nightwork_column_chart").empty();
            $("#check_div").empty();
            $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
            $("#check_div_copy").empty();
            $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
            Nightwork_column_chart(NightworkColumnChartDatas, NightworkChart9SeriesData, NightworkChart9SectionData, NightworkYAxisTitle, NightworkColumnChartTitle);
            for (var i=0; i< chart9SeriesData.length; i++) {
                chart9SeriesData[i].visible = true;
            }
            $("#search_con1").css("display", "block");
            $("#bagbtn").css("display","block");
            $("#left_but").css("display","inline-block");
            // $("#off_search_chart_contain").css("margin-top",'-2.3%');
        }
    });
}

// 只是封装成一个function
function show_nightwork_modal(attendanceInfo, series_name, this_date, this_color) {

    createTbody("specific_nightwork_tab");
    $("#Leader").html(series_name);
    $("#Time").html(this_date);
    $("#nightwork_caption").css("backgroundColor", this_color);
    $("#specific_nightwork_tab").css("borderColor", this_color);

    for (var i = 0; i < attendanceInfo.length; i++) {
        //var days_ontime = attendanceInfo[i].a_totaldays - attendanceInfo[i].a_dutydays
        $("#specific_nightwork_tab").append("<tr><td>" + attendanceInfo[i].a_employee + "</td><td>" + attendanceInfo[i].a_name + "</td><td>" + attendanceInfo[i].a_maxlastcard + "</td><td>"
            + attendanceInfo[i].a_avglastcard + "</td><td>" + parseFloat(attendanceInfo[i].a_totalhours).toFixed(2) + "</td><td>" + attendanceInfo[i].a_totaldays + "</td><td>" + parseFloat(attendanceInfo[i].a_avghours).toFixed(2) +
            "</td><td>" + parseFloat(attendanceInfo[i].a_maxhours).toFixed(2) + "</td><td>" + attendanceInfo[i].a_offduty +"</td><td>" + attendanceInfo[i].a_unoffduty +"</td><td>" +
            attendanceInfo[i].a_offdutyper +"%</td><td>" + attendanceInfo[i].a_unoffdutyper +"%</td></tr>");
    }

}

// 用于考勤模块第三层弹框  点击表格的表头自动按照被点击的那一项排序
function click_nightwork_th(all_attendanceInfo,series_name, this_date, this_color) {
    $(".nightwork_th_bac").click(function () {
        var the_key = $(this).attr('name');
        //console.log('this click name:', this, $(this).attr('name'));
        show_nightwork_modal(all_attendanceInfo[the_key],series_name, this_date, this_color)
    })
}


// 按照日期 每月的每个leader下的晚點下班人次统计
function draw_chart9(seriesData, sectionData, yAxisTitle, chart_title, plotOptionsValue) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */

    NightworkseriesData = seriesData;
    NightworksectionData = sectionData;
    NightworkyAxisTitle = yAxisTitle;
    Nightworkchart_title = chart_title;
    NightworkplotOptionsValue = plotOptionsValue;

    for (var i=0; i<seriesData.length; i++) {
        // name data
        var dataLen = seriesData[i].data.length;
        var firstList = seriesData[i].data[dataLen - 1];
        var secondeList = seriesData[i].data[dataLen - 2];
        var difference = firstList[1] - secondeList[1];

        $("#downLoadTable").append("<tr>" + 
            "<td>" + seriesData[i].name + "</td>" + 
            "<td>" + firstList[1] + "</td>" + 
            "<td>" + difference.toFixed(2) + "</td>" + 
            "</tr>");
    }
    Highcharts.setOptions({
        lang: {
            shortMonths: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
    });

    $("input[type='checkbox']").prop("checked", false);
    $("#nightwork_line_chart").highcharts("StockChart", {
        navigator:{
            xAxis: {
                labels: {
                    useHTML: true,

                }
            },
        },
        rangeSelector: {
            allButtonsEnabled: true,
            buttons: [
                {
                    type: "month",
                    count: 6,
                    text: "6m"
                },
                {
                    type: "year",
                    count: 1,
                    text: "1y"
                },
                {
                    type: "all",
                    text: "All"
                }
            ],
            selected: 1
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "晚點下班人數",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        colors: ["#CC99CC", "#99CC99", "#669999", "#009966", "#CC6600", "#CCCC33", "#336699", "#FF6666", "#999999", "#009933"],
        chart: {
            backgroundColor: "rgba(0,0,0,0)",
            zoomType: "xy",
            style: {
                fontSize: "18px"
            }
        },
        title: {
            text: chart_title,
            useHTML: true,
            style: {
                fontSize: "20px",
            }
        },
        credits: {
            enabled: false
        },
        legend: {
            enabled: true
        },
        xAxis: {
            type: "datetime",
            dateTimeLabelFormats: {
                day: "%Y<br/>%m-%d",
                month: "%Y-%m",
                year: "%Y"
            },
            labels: {
                useHTML: true,
            }
        },
        yAxis: {
            labels: {
                useHTML: true,
                formatter: function () {
                    return this.value;
                }
            },
            title: {
                text: yAxisTitle
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true,
                    crop: false,
                    format: "{point.y:2f}" + plotOptionsValue,
                    // allowOverlap:true
                    //overflow: 'none',
                    //format:'{point.y:.2f}%',
                },
                point: {
                    events: {
                        click: function () {
                            $('.nightwork_th_bac').css("background-color",'rgba(0, 0, 0, 0)')
                            $('.nightwork_th_bac').css("font-size",'1.6rem')
                            $('.nightwork_th_bac').eq(1).css("background-color",'rgb(222, 146, 141)')
                            var thisYearTimestamp = new Date("2018-05-1 00:00:00").getTime();
                            if (this.x >= thisYearTimestamp) {
                                $("#search_chart_contain").css("display", "none");
                                $("#nightwork_column_chart").css("display", "none");
                                $("#section_search_chart_contain").css("display", "block");
                                $("#check_div").empty();
                                $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
                                $("#check_div_copy").empty();
                                $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");

                                var all_attendanceInfo = getAttendanceInfo(this.x, this.colorIndex);
                                leader_name = this.series.userOptions.name;
                                b = all_attendanceInfo[1];
                                sectionData_list = [];
                                for (i in all_attendanceInfo){
                                    d = all_attendanceInfo[i];
                                    for (j in sectionData)
                                        if (d == sectionData[j].name){
                                            sectionData_list.push(sectionData[j]);
                                            break
                                        }
                                };
                                draw_chart9_section(sectionData_list, yAxisTitle, chart_title, plotOptionsValue, leader_name);

                            }
                            else {
                                alert("该节点没有数据");
                            }
                        }
                    }
                },
            },
            series: {
                cursor: "pointer",
                showInLegend: true,
                // allowPointSelect: true,
                marker: {
                    radius: 10
                },
                states: {
                    hover: {
                        lineWidthPlus: 15
                    }
                }
            }

        },
        tooltip: {
            split: false,
            shared: false,
            xDateFormat: "<br/>" + "%Y-%m-%d",
            style: {
                fontSize: "15px"
            }
        },
        series: seriesData
    },function (c) {
        checklegend(c);
    });

    // 点击后退按钮对应的函数(考勤第三层后退到第二层)
     $("#off_search_chart_contain_section").click(function () {
         setTimeout(function () {
            /* 重新畫圖，避免下載圖后空白 */
            if ($("#search_chart_contain").css("display") === 'none') {
                $("#section_search_chart_contain").css("display", "none");
                $("#search_chart_contain").css("display", "block");
                $("#nightwork_line_chart").empty();
                $("#check_div").empty();
                $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
                $("#check_div_copy").empty();
                $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");

                draw_chart9(NightworkseriesData, NightworksectionData, NightworkyAxisTitle, Nightworkchart_title, NightworkplotOptionsValue);
                for (var i=0; i< chart9SeriesData.length; i++) {
                chart9SeriesData[i].visible = true;
            }
            }
        }, 600)
    });
}

//*********************************************************************************************************************//
// 按照日期 每月的每个leader下的晚點下班人次统计
function draw_chart9_section(seriesData, yAxisTitle, chart_title, plotOptionsValue, leader_name) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    chart_title = chart_title.split("EERF")[1];
    for (var i=0; i<seriesData.length; i++) {
        // name data
        var dataLen = seriesData[i].data.length;
        var firstList = seriesData[i].data[dataLen - 1];
        var secondeList = seriesData[i].data[dataLen - 2];
        var difference = firstList[1] - secondeList[1];

        $("#downLoadTable").append("<tr>" +
            "<td>" + seriesData[i].name + "</td>" +
            "<td>" + firstList[1] + "</td>" +
            "<td>" + difference.toFixed(2) + "</td>" +
            "</tr>");
    }
    Highcharts.setOptions({
        lang: {
            shortMonths: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
    });

    $("input[type='checkbox']").prop("checked", false);
    $("#section_nightwork_line_chart").highcharts("StockChart", {
        rangeSelector: {
            allButtonsEnabled: true,
            buttons: [
                {
                    type: "month",
                    count: 6,
                    text: "6m"
                },
                {
                    type: "year",
                    count: 1,
                    text: "1y"
                },
                {
                    type: "all",
                    text: "All"
                }
            ],
            selected: 1
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "【" + leader_name +  "】 team" + "晚點下班人數",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        colors: ["#CC99CC", "#99CC99", "#669999", "#009966", "#CC6600", "#CCCC33", "#336699", "#FF6666", "#999999", "#009933"],
        chart: {
            backgroundColor: "rgba(0,0,0,0)",
            zoomType: "xy",
            style: {
                fontSize: "18px"
            }
        },
        title: {
            text:  "【" + leader_name +  "】 team" + chart_title,
            useHTML: true,
            style: {
                fontSize: "20px",
            }
        },
        credits: {
            enabled: false
        },
        legend: {
            enabled: true
        },
        xAxis: {
            type: "datetime",
            dateTimeLabelFormats: {
                day: "%Y<br/>%m-%d",
                month: "%Y-%m",
                year: "%Y"
            },
            labels: {
                useHTML: true,
            }
        },
        yAxis: {
            labels: {
                formatter: function () {
                    return this.value;
                }
            },
            title: {
                text: yAxisTitle
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true,
                    crop: false,
                    format: "{point.y:2f}" + plotOptionsValue,
                    // allowOverlap:true
                    //overflow: 'none',
                    //format:'{point.y:.2f}%',
                },
                point: {
                    events: {
                        click: function () {
                            $('.nightwork_th_bac').css("background-color",'rgba(0, 0, 0, 0)')
                            $('.nightwork_th_bac').css("font-size",'1.6rem')
                            $('.nightwork_th_bac').eq(1).css("background-color",'rgb(222, 146, 141)')
                            var thisYearTimestamp = new Date("2018-05-1 00:00:00").getTime();
                            if (this.x >= thisYearTimestamp) {
                                var all_attendanceInfo = getAttendanceInfoFour(this.x, this.colorIndex);
                                // console.log('attendanceInfo:',all_attendanceInfo);
                                $("#nightwork_modal").modal();
                                show_nightwork_modal(all_attendanceInfo['a_avglastcard'],this.series.name,this.key.slice(5),this.color);
                                click_nightwork_th(all_attendanceInfo,this.series.name,this.key.slice(5),this.color);
                            }
                            else {
                                alert("该节点没有数据");
                            }
                        }
                    }
                },
            },
            series: {
                cursor: "pointer",
                showInLegend: true,
                // allowPointSelect: true,
                marker: {
                    radius: 10
                },
                states: {
                    hover: {
                        lineWidthPlus: 15
                    }
                }
            }

        },
        tooltip: {
            split: false,
            shared: false,
            xDateFormat: "<br/>" + "%Y-%m-%d",
            style: {
                fontSize: "15px"
            }
        },
        series: seriesData
    },function (c) {
        checklegend(c);
    });
    $('.nightwork_th_bac').click(function(){
        if ($(this).css("background-color") === 'rgba(0, 0, 0, 0)') {
             $('.nightwork_th_bac').css("background-color",'rgba(0, 0, 0, 0)')
             $('.nightwork_th_bac').css("font-size",'1.6rem')
             $(this).css("background-color",'rgb(222, 146, 141)')
             $(this).css("font-size",'18px')
             $(this).css("box-shadow",'0px 0px 7px 2px #332e2e inset')
        }
    })

}
//*********************************************************************************************************************//

// 每月的 整个EERF人均晚班天次统计的柱状图
function Eveningtrips_column_chart(dataList, chart10DataList, chart10DataSectionList) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    Eveningtrips_Datas = dataList;
    Eveningtrips_chart10Datas = chart10DataList;
    Highcharts.setOptions({
        lang: {
            shortMonths: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
    });

    Highcharts.stockChart("eveningtrips_column_chart", {
        rangeSelector: {
            allButtonsEnabled: true,
            buttons: [
                {
                    type: "month",
                    count: 6,
                    text: "6m"
                },
                {
                    type: "year",
                    count: 1,
                    text: "1y"
                },
                {
                    type: "all",
                    text: "All"
                }
            ],
            selected: 1
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "晚班天數",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        title: {
            text: "晚班天數",
            style: {
                fontSize: "20px",
            }
        },
        xAxis: {
            type: "datetime",
            dateTimeLabelFormats: {
                day: "%Y<br/>%m-%d",
                month: "%Y-%m",
                year: "%Y"
            }
        },
        yAxis: {
            title: {
                text: "人数(人)"
            }
        },
        tooltip: {
            xDateFormat: "%B %Y" + "<br/>" + "%Y-%m-%d",
        },
        plotOptions: {
            column: {
                dataLabels: {
                    enabled: true,
                    crop: false,
                    overflow: "none",
                    format: "{point.y:2f}",
                },
                point: {
                    events: {
                        click: function () {
                            var thisYearTimestamp = new Date("2018-01-1 00:00:00").getTime();
                            if (this.x >= thisYearTimestamp) {
                                $("#search_chart_contain").css("display", "block");
                                $("#eveningtrips_column_chart").css("display", "none");
                                $("#section_search_chart_contain").css("display", "none");
                                $("#check_div").empty();
                                $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
                                $("#check_div_copy").empty();
                                $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");

                                draw_chart10(chart10DataList, chart10DataSectionList);
                            }
                        }
                    }
                }
            },
            series: {
                showInLegend: true
            }
        },
        chart: {
            backgroundColor: "rgba(0,0,0,0)",
        },
        credits: {
            enabled: false
        },
        series: dataList
    });
    // 点击后退按钮对应的函数(考勤第二层后退到第一层)
    $("#off_search_chart_contain").click(function () {
        /* 重新畫圖，避免下載圖后空白 */
        if ($("#eveningtrips_column_chart").css("display") === 'none') {
            $("#search_chart_contain").css("display", "none");
            $("#eveningtrips_column_chart").css("display", "block");
            $("#eveningtrips_column_chart").empty();
            $("#check_div").empty();
            $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
            $("#check_div_copy").empty();
            $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");

            for (var i=0; i< chart10DataList.length; i++) {
                chart10DataList[i].visible = true;
            }
            Eveningtrips_column_chart(Eveningtrips_Datas, Eveningtrips_chart10Datas, chart10DataSectionList);
        }
    });

}

function show_eveningtrips_modal(attendanceInfo, series_name, this_date, this_color) {
    createTbody("specific_eveningtrips_tab");
    $("#Time").html(this_date);
    $("#Leader").html(series_name);
    $("#eveningtrips_caption").css("backgroundColor", this_color);
    $("#specific_eveningtrips_tab").css("borderColor", this_color);
    for (var i = 0; i < attendanceInfo.length; i++) {
        $("#specific_eveningtrips_tab").append("<tr><td>" + attendanceInfo[i].a_employee + "</td><td>" + attendanceInfo[i].a_name + "</td><td>" + attendanceInfo[i].a_nightnum + "</td><td>"
            +  parseFloat(attendanceInfo[i].a_totalhours).toFixed(2) + "</td><td>" + attendanceInfo[i].a_totaldays + "</td><td>" + parseFloat(attendanceInfo[i].a_avghours).toFixed(2) +
            "</td><td>" + parseFloat(attendanceInfo[i].a_maxhours).toFixed(2) + "</td></tr>");
    }
}

function click_eveningtrips_th(all_attendanceInfo,series_name, this_date, this_color) {
    $(".nightwork_th_bac").click(function () {
        // console.log('this click name:',this,$(this).attr('name'));
        var the_key = $(this).attr('name');

        show_eveningtrips_modal(all_attendanceInfo[the_key],series_name, this_date, this_color)
    })
}

// 每月的 每个leader下的人均晚班天次
function draw_chart10(seriesData, sectionData) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    seriesData_data = seriesData;
    Highcharts.setOptions({
        lang: {
            shortMonths: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
    });

    $("input[type='checkbox']").prop("checked", false);
    $("#eveningtrips_line_chart").highcharts("StockChart", {
        rangeSelector: {
            allButtonsEnabled: true,
            buttons: [
                {
                    type: "month",
                    count: 6,
                    text: "6m"
                },
                {
                    type: "year",
                    count: 1,
                    text: "1y"
                },
                {
                    type: "all",
                    text: "All"
                }
            ],
            selected: 1
        },
        colors: ["#CC99CC", "#99CC99", "#669999", "#009966", "#CC6600", "#CCCC33", "#336699", "#FF6666", "#999999", "#009933"],
        chart: {
            backgroundColor: "rgba(0,0,0,0)",
            zoomType: "xy",
            style: {
                fontSize: "18px"
            }
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "晚班天數",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        title: {
            text: "人均晚班天次",
            style: {
                fontSize: "20px",
            }
        },
        credits: {
            enabled: false
        },
        legend: {
            enabled: true
        },
        xAxis: {
            type: "datetime",
            dateTimeLabelFormats: {
                day: "%Y<br/>%m-%d",
                month: "%Y-%m",
                year: "%Y"
            }
        },
        yAxis: {
            labels: {
                formatter: function () {
                    return this.value;
                }
            },
            title: {
                text: "天次(天)"
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true,
                    crop: false,
                    // allowOverlap:true
                    //overflow: 'none',
                    //format:'{point.y:.2f}%',
                },
                point: {
                    events: {
                        click: function () {
                            var thisYearTimestamp = new Date("2018-05-1 00:00:00").getTime();
                            if (this.x >= thisYearTimestamp) {
                                $("#search_chart_contain").css("display", "none");
                                $("#eveningtrips_column_chart").css("display", "none");
                                $("#section_search_chart_contain").css("display", "block");
                                $("#check_div_copy").empty();
                                $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
                                $("#check_div").empty();
                                $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
                                var all_attendanceInfo = getAttendanceInfo(this.x, this.colorIndex);
                                leader_name = this.series.userOptions.name;
                                b = all_attendanceInfo[1];
                                sectionData_list = [];
                                for (i in all_attendanceInfo){
                                    d = all_attendanceInfo[i];
                                    for (j in sectionData)
                                        if (d == sectionData[j].name){
                                            sectionData_list.push(sectionData[j]);
                                            break
                                        }
                                };
                                draw_chart10_next(sectionData_list, leader_name)
                            }
                            else {
                                alert("该节点没有数据");
                            }
                        }
                    }
                }
            },
            series: {
                cursor: "pointer",
                showInLegend: true,
                // allowPointSelect: true,
                marker: {
                    radius: 10
                },
                states: {
                    hover: {
                        lineWidthPlus: 15
                    }
                }
            }
        },
        tooltip: {
            split: false,
            shared: false,
            xDateFormat: "<br/>" + "%Y-%m-%d",
            style: {
                fontSize: "15px"
            }
        },
        series: seriesData
    },function (c) {
        checklegend(c);
    });
    // 点击后退按钮对应的函数(考勤第三层后退到第二层)
     $("#off_search_chart_contain_section").click(function () {
         setTimeout(function () {
            /* 重新畫圖，避免下載圖后空白 */
            if ($("#search_chart_contain").css("display") === 'none') {
                $("#section_search_chart_contain").css("display", "none");
                $("#search_chart_contain").css("display", "block");
                $("#section_eveningtrips_line_chart").empty();
                $("#check_div").empty();
                $("#check_div").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");
                $("#check_div_copy").empty();
                $("#check_div_copy").append("<input class='check_legend' type='checkbox' checked='checked'><label class='checkall' for='check_all'>取消選取全部</label>");

                // for (var i=0; i< seriesData.length; i++) {
                //     seriesData[i].visible = true;
                // }
                draw_chart10(seriesData_data, sectionData);
            }
        }, 600)
    });
}

/******************************************************************************************************/
// 每月的 每个leader下的对应科级人均晚班天次
function draw_chart10_next(seriesData, leader_name) {
    /**
     * @method
     * @param {Type} [{},{}...]
     * @returns
     * @desc 传递highchart所需的参数，画图
     */
    Highcharts.setOptions({
        lang: {
            shortMonths: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
    });

    $("input[type='checkbox']").prop("checked", false);
    $("#section_eveningtrips_line_chart").highcharts("StockChart", {
        rangeSelector: {
            allButtonsEnabled: true,
            buttons: [
                {
                    type: "month",
                    count: 6,
                    text: "6m"
                },
                {
                    type: "year",
                    count: 1,
                    text: "1y"
                },
                {
                    type: "all",
                    text: "All"
                }
            ],
            selected: 1
        },
        colors: ["#CC99CC", "#99CC99", "#669999", "#009966", "#CC6600", "#CCCC33", "#336699", "#FF6666", "#999999", "#009933"],
        chart: {
            backgroundColor: "rgba(0,0,0,0)",
            zoomType: "xy",
            style: {
                fontSize: "18px"
            }
        },
        exporting: {
            url: "//export.highcharts.com.cn",
            filename: "【" + leader_name +  "】 " + "team晚班天數",
            enabled: true,
            sourceWidth: 1200,
            sourceHeight: 600
        },
        title: {
            text: "【" + leader_name +  "】 " + "team人均晚班天次",
            style: {
                fontSize: "20px",
            }
        },
        credits: {
            enabled: false
        },
        legend: {
            enabled: true
        },
        xAxis: {
            type: "datetime",
            dateTimeLabelFormats: {
                day: "%Y<br/>%m-%d",
                month: "%Y-%m",
                year: "%Y"
            }
        },
        yAxis: {
            labels: {
                formatter: function () {
                    return this.value;
                }
            },
            title: {
                text: "天次(天)"
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true,
                    crop: false,
                    // allowOverlap:true
                    //overflow: 'none',
                    //format:'{point.y:.2f}%',
                },
                point: {
                    events: {
                        click: function () {
                            $('.nightwork_th_bac').css("background-color",'rgba(0, 0, 0, 0)')
                            $('.nightwork_th_bac').css("font-size",'1.6rem')
                            $('.nightwork_th_bac').eq(0).css("background-color",'rgb(222, 146, 141)')
                            var thisYearTimestamp = new Date("2018-05-1 00:00:00").getTime();
                            if (this.x >= thisYearTimestamp) {
                                var all_attendanceInfo = getAttendanceInfoFour(this.x, this.colorIndex);
                                $("#eveningtrips_modal").modal();
                                // var attendanceInfo = all_attendanceInfo['a_nightnum'];
                                show_eveningtrips_modal(all_attendanceInfo['a_nightnum'],this.series.name,this.key.slice(5),this.color);
                                click_eveningtrips_th(all_attendanceInfo,this.series.name,this.key.slice(5),this.color);
                            }
                            else {
                                alert("该节点没有数据");
                            }
                        }
                    }
                }
            },
            series: {
                cursor: "pointer",
                showInLegend: true,
                // allowPointSelect: true,
                marker: {
                    radius: 10
                },
                states: {
                    hover: {
                        lineWidthPlus: 15
                    }
                }
            }
        },
        tooltip: {
            split: false,
            shared: false,
            xDateFormat: "<br/>" + "%Y-%m-%d",
            style: {
                fontSize: "15px"
            }
        },
        series: seriesData
    },function (c) {
        checklegend(c);
    });
$('.nightwork_th_bac').click(function(){
        if ($(this).css("background-color") === 'rgba(0, 0, 0, 0)') {
             $('.nightwork_th_bac').css("background-color",'rgba(0, 0, 0, 0)')
             $('.nightwork_th_bac').css("font-size",'1.6rem')
             $(this).css("background-color",'rgb(222, 146, 141)')
             $(this).css("font-size",'18px')
             $(this).css("box-shadow",'0px 0px 7px 2px #332e2e inset')
        }
    })
}

