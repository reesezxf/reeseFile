var isclick=true;
sum_team();
color_check();

$("#btn_start").click(function () {
    sum_team(false);
});


$("#save_ajax").click(function () {
    var row_data = {};
    var info = $("#text_info").val();
    $(".bonus_report").each(function () {
        var row = "";
        var row_list = [];
        $(this).find('td').each(function() {
            row = row + "@@" +$(this).html();
            row_list.push($(this).html())
        });
        if (row_list.length > 1) {
            var team = $(this).children(".functionteam").html();
            row_data[team] = row;
        }
    });
    $(".bonus_reportdepartment").each(function () {
        var row = "";
        var row_list = [];
        $(this).find('td').each(function() {
            row = row + "@@" +$(this).html();
            row_list.push($(this).html())
        });
        if (row_list.length > 1) {
            var leader = $(this).children(".department_leader").html();
            row_data[leader] = row;
        }
    });
    row_data["info"] = info;
    row_data["total_money"] = $("#ipt_z").val();
    row_data["personal_money"] = $("#ipt_zjj").val();
    row_data["team_money"] = $("#ipt_td").val();
    row_data["other_money"] = $("#ipt_qt").val();

    row_data["gs_weight_t"] = $("#gs_weight").html();
    row_data["patent_weight_t"] = $("#patent_weight").html();
    row_data["tax_weight_t"] = $("#taxdeduction_weight").html();
    row_data["gs_weight_d"] = $("#gs_weightdepartment").html();
    row_data["patent_weight_d"] = $("#patent_weightdepartment").html();
    row_data["tax_weight_d"] = $("#taxdeduction_weightdepartment").html();

    row_data["hr_d"] = $("#hr_percentagedepartment").html();
    row_data["other_d"] = $("#percentage_1department").html();
    row_data["task_force_d"] = $("#task_force_percentagedepartment").html();
    row_data["other_t"] = $("#percentage_1").html();
    row_data["task_force_t"] = $("#task_force_percentage").html();

    row_data["proposal_t"] = $("#proposal_percentage").html();
    row_data["ee_t"] = $("#exceed_expected_percentage").html();
    row_data["idl_t"] = $("#idl_percentage").html();
    row_data["duty_t"] = $("#duty_work_percentage").html();
    row_data["10_5_t"] = $("#over_10_5_time_percentage").html();
    row_data["night_t"] = $("#night_work_percentage").html();
    row_data["travel_abroad_t"] = $("#travel_abroad_percentage").html();
    row_data["travel_cn_t"] = $("#travel_cn_percentage").html();
    row_data["leave_t"] = $("#leave_percentage").html();

    row_data["proposal_d"] = $("#proposal_percentagedepartment").html();
    row_data["ee_d"] = $("#exceed_expected_percentagedepartment").html();
    row_data["idl_d"] = $("#idl_percentagedepartment").html();
    row_data["duty_d"] = $("#duty_work_percentagedepartment").html();
    row_data["10_5_d"] = $("#over_10_5_time_percentagedepartment").html();
    row_data["night_d"] = $("#night_work_percentagedepartment").html();
    row_data["travel_abroad_d"] = $("#travel_abroad_percentagedepartment").html();
    row_data["travel_cn_d"] = $("#travel_cn_percentagedepartment").html();
    row_data["leave_d"] = $("#leave_percentagedepartment").html();
    $.ajax({
        type: "POST",
        async: false,
        url: "/save_bonus/",
        dataType: "json",
        data: row_data,
        traditional: true,
        success: function (ret) {
            // data = [];
            alert("保存成功")
        },
        error: function () {
            alert("Error");
        }
    });
});

$("#btn_save").click(function () {
    $("#text_info").val("");
});

$("#btn_load").click(function () {
    $.ajax({
        type: "POST",
        async: false,
        url: "/get_table_info/",
        dataType: "json",
        data: {"info":"get_table_info"},
        traditional: true,
        success: function (ret) {
            $("#show_tbody").empty();
            // data = [];
            for (var i=0;i<ret.data.length;i++) {
                $("#show_tbody").append('<tr ng-repeat="data in datas"><td><div class="checkbox icheck-emerland"><input class="load_checkbox" type="checkbox" id="' + ret.data[i][2] + '" value="' + "666" + '"/><label for="' + ret.data[i][2] + '"></label></div></td><td style="display:table-cell; vertical-align:middle">' + ret.data[i][0] + '</td><td style="display:table-cell; vertical-align:middle">' + ret.data[i][1] + '</td><td style="padding-top: 16px;"><a onclick="single_del(this);" href="#" id="@@'+ret.data[i][2]+'" class="del" style="font-size: 16px;font-family: 微软雅黑;color: #d6453a;">刪除</a></td></tr>')

            }
            console.log(ret.data)
        },
        error: function () {
            alert("Error");
            console.log("getAttendanceInfo ajax fail...");
        }
    });


});


$("#click_delete").click(function () {
    var checked_id = "";
    $("input[type=checkbox].load_checkbox").each(function(){
        if (this.checked) {
            checked_id = checked_id + "@@" + $(this).attr("id");
            $(this).parent().parent().parent('tr').remove();
        }
    });
    if (checked_id.length > 0){
        $.ajax({
        type: "POST",
        async: false,
        url: "/del_bonus/",
        dataType: "json",
        data: {"checked_id":checked_id},
        success: function (ret) {
            alert("刪除成功");

            console.log(ret.data)
        },
        error: function () {
            alert("Error");
        }
    });
    }else {
        alert("請選擇需要刪除的數據")
    }
});


function single_del(a) {
    var id = $(a).attr("id");
    $.ajax({
        type: "POST",
        async: false,
        url: "/del_bonus/",
        dataType: "json",
        data: {"checked_id":id},
        success: function (ret) {
            alert("刪除成功");
            $("#"+id.split("@@")[1]).parent().parent().parent('tr').remove();

        },
        error: function () {
            alert("Error");
        }
    });
}



$("#btn_loadbonus").click(function () {
    var checked_id = [];
    $("input[type=checkbox].load_checkbox").each(function(){
        if (this.checked) {
            checked_id.push($(this).attr("id"));
        }
    });
    if (checked_id.length == 1){
        var left_1 = $("#div_table").scrollLeft();
         var top=$("#div_table").scrollTop();//获取滚动的距离
        setTimeout(function () {
        var trs_666 = $("#div_table table tr");
                    trs_666.each(function (i) {
                        $(this).children().eq(0).css({
                            "position": "relative",
                            "top": "0px",
                            "left": left_1,
                            "background-color": "#ece8e8",
                            "z-index":"6666"
                        });
                    });
         var trs_td1_1 = $("#table_body_team tr:nth-child(1) td:nth-child(1)");
                    trs_td1_1.each(function (i) {
                        $(this).css({
                            "position": "relative",
                            "top": top,
                            "left": left_1,
                            "background-color": "#ece8e8",
                            "z-index":"999999"
                        });
                    });

                    var trs_td2_2 = $("#table_body_team tr:nth-child(2) td:nth-child(1)");
                    trs_td2_2.each(function (i) {
                        $(this).css({
                            "position": "relative",
                            "top": top,
                            "left": left_1,
                            "background-color": "#ece8e8",
                            "z-index":"999999"
                        });
                    });
                    var trs_td3_3 = $("#table_body_team tr:nth-child(3) td:nth-child(1)");
                    trs_td3_3.each(function (i) {
                        $(this).css({
                            "position": "relative",
                            "top": top,
                            "left": left_1,
                            "background-color": "#ece8e8",
                            "z-index":"999999"
                        });
                    });
                    var trs_td4_4 = $("#table_body_team tr:nth-child(4) td:nth-child(1)");
                    trs_td4_4.each(function (i) {
                        $(this).css({
                            "position": "relative",
                            "top": top,
                            "left": left_1,
                            "background-color": "#ece8e8",
                            "z-index":"999999"
                        });
                    });
    },300);
        $.ajax({
        type: "POST",
        async: false,
        url: "/get_bonus_report/",
        dataType: "json",
        data: {"checked_id":checked_id[0]},
        success: function (response) {
            // $("div").remove("#oDivL_table_score_team");

            $('.bonus_report').each(function () {
                $(this).remove();
            });
            $('.bonus_reportdepartment').each(function () {
                $(this).remove();
            });
            var department_list = response.department;
            var team_name_list = response.team_name;
            for(var i = 0;i < team_name_list.length;i++){
                var data =  response[team_name_list[i].b_team];
                $("#table_body_team").append('<tr class="bonus_report">\n' +
                    '                            <td style="background: white;" class="functionteam">'+team_name_list[i].b_team+'</td>\n' +
                    '                            <td style="background: white;">'+data[1]+'</td>\n' +
                    '                            <td style="background: white;">'+data[2]+'</td>\n' +
                    '                            <td style="background: white;" class="gs_num" id="'+data[0]+'gs">'+data[4]+'</td>\n' +
                    '                            <td style="background: white;" id="'+data[0]+'gs_weight">'+data[5]+'</td>\n' +
                    '                            <td class="gs_rate" id="'+data[0]+'_gs_rate" style="background: white;color: #DD0CC2;font-weight: 700;">'+data[6]+'</td>\n' +
                    '                            <td class="patent_num" id="'+data[0]+'patent_num"  style="background: white;color: #000000">'+data[7]+'</td>\n' +
                    '                            <td style="background: white;" id="'+data[0]+'patent_num_weight">'+data[8]+'</td>\n' +
                    '                            <td class="patent_rate" id="'+data[0]+'_patent_rate" style="background: white;color: #DD0CC2;font-weight: 700;">'+data[9]+'</td>\n' +
                    '                            <td class="taxdeduction" id="'+data[0]+'taxdeduction" style="background: white;color: #000000">'+data[10]+'</td>\n' +
                    '                            <td style="background: white;" id="'+data[0]+'taxdeduction_weight">'+data[11]+'</td>\n' +
                    '                            <td style="background: white;color: #1986dc;font-weight: 700;" class="proposal" id="'+data[0]+'_proposal">'+data[12]+'</td>\n' +
                    '                            <td contenteditable="true" style="background: white;color: #000000" class="exceed_expected" id="'+data[0]+'_exceed_expected" hc="'+data[40]+'">'+data[13]+'</td>\n' +
                    '                            <td style="background: white;" id="'+data[0]+'_exceed_expected_point" class="exceed_expected_point">'+data[14]+'</td>\n' +
                    '                            <td style="background: white;color: #000000" class="idl" id="'+data[0]+'_idl">'+data[15]+'</td>\n' +
                    '                            <td class="customer" id="'+data[0]+'_customer" style="background: white;color: #1986dc;font-weight: 700;">'+data[16]+'</td>\n' +
                    '                            <td style="background: white;" class="duty_work" id="'+data[0]+'_duty_work">'+data[17]+'</td>\n' +
                    '                            <td style="background: white;color: #DD0CC2;font-weight: 700;" class="duty_work_hc" id="'+data[0]+'_duty_work_hc">'+data[18]+'</td>\n' +
                    '                            <td style="background: white;" class="over_10_5_time" id="'+data[0]+'_over_10_5_time">'+data[19]+'</td>\n' +
                    '                            <td style="background: white;color: #DD0CC2;font-weight: 700;" class="over_10_5_time_hc" id="'+data[0]+'_over_10_5_time_hc">'+data[20]+'</td>\n' +
                    '                            <td style="background: white;" class="night_work" id="'+data[0]+'_night_work">'+data[21]+'</td>\n' +
                    '                            <td style="background: white;color: #DD0CC2;font-weight: 700;" class="night_work_hc" id="'+data[0]+'_night_work_hc">'+data[22]+'</td>\n' +
                    '                            <td style="background: white;" class="travel_abroad" id="'+data[0]+'_travel_abroad">'+data[23]+'</td>\n' +
                    '                            <td style="background: white;color: #DD0CC2;font-weight: 700;" class="travel_abroad_hc" id="'+data[0]+'_travel_abroad_hc">'+data[24]+'</td>\n' +
                    '                            <td style="background: white;" class="travel_cn" id="'+data[0]+'_travel_cn">'+data[25]+'</td>\n' +
                    '                            <td style="background: white;color: #DD0CC2;font-weight: 700;" class="travel_cn_hc" id="'+data[0]+'_travel_cn_hc">'+data[26]+'</td>\n' +
                    '                            <td style="background: white;">'+data[27]+'</td>\n' +
                    '                            <td class="leave_point" id="'+data[0]+'_leave_point">'+data[28]+'</td>\n' +
                    '                            <td style="background: white;color: #1986dc;font-weight: 700;" class="dimission_percentage" id="'+data[0]+'_dimission_percentage">'+data[29]+'</td>\n' +
                    '                            <td style="background: white;color: #1986dc;font-weight: 700;" class="attendance_percentage" id="'+data[0]+'_attendance_percentage">'+data[30]+'</td>\n' +
                    '                            <td style="background: white;color: #DD0CC2;font-weight: 700;" class="teamloading" id="'+data[0]+'_teamloading">'+data[39]+'</td>\n' +
                    '                            <td style="background: white;" class="total_percentage" id="'+data[0]+'_total_percentage">'+data[31]+'</td>\n' +
                    '                            <td contenteditable="true" style="background: white;color: #000000" class="task_force_num" id="'+data[0]+'_task_force_num">'+data[32]+'</td>\n' +
                    '                            <td style="background: white;color: #1986dc;font-weight: 700;" class="task_force_point" id="'+data[0]+'_task_force_point">'+data[33]+'</td>\n' +
                    '                            <td  style="width: 150px;background:  white;" class="all_total" id="'+data[0]+'_all_total">'+data[34]+'</td>\n' +
                    '                            <td  style="width: 150px;background:  white;"  id="'+data[0]+'_all_total_money">'+data[35]+'</td>\n' +
                    '                            <td style="display: none;background: white;color: #252422;font-weight: 700;">0</td>\n' +
                    '                            <td style="display: none;background: white;color: #252422;font-weight: 700;">0</td>\n' +
                    '                            <td style="display: none;background: white;width: 150px;color: #000000;">0</td>\n' +
                    '                            <td style="display: none;background: white;width: 150px;color: #000000;">0</td>\n' +
                    '                            <td contenteditable="true" style="background: white;color: #000000" class="violation" id="'+data[0]+'_violation">'+data[36]+'</td>\n' +
                    '                            <td contenteditable="true" style="background: white;color: #000000" class="below_quality" id="'+data[0]+'_below_quality">'+data[37]+'</td>\n' +
                    '                            <td style="background: white;width: 150px" class="finally_money" id="'+data[0]+'_finally_money">'+data[38]+'</td>\n' +
                    '                        </tr>')
            };
            $("#table_body_team").append('<tr style="font-size: 15px;font-weight: 700;" class="bonus_report">\n' +
                '                        <td style="background: white;color: darkred;font-size: 16px;">EERF Total</td>\n' +
                '                        <td></td>\n' +
                '                        <td></td>\n' +

                '                        <td class="total_gs_num"></td>\n' +
                '                        <td class="total_gs_weight"></td>\n' +
                '                        <td ></td>\n' +
                '                        <td class="total_patent_num"></td>\n' +
                '                        <td class="total_patent_weight"></td>\n' +
                '                        <td ></td>\n' +
                '                        <td class="total_taxdeduction_num"></td>\n' +
                '                        <td class="total_taxdeduction_weight"></td>\n' +
                '                        <td class="total_proposal_percentage"></td>\n' +
                '                        <td class="total_exceed_expected"></td>\n' +
                '                        <td class="total_exceed_expected_point"></td>\n' +
                '                        <td class="total_idl"></td>\n' +
                '                        <td class="total_customer"></td>\n' +
                '                        <td class="total_duty_work"></td>\n' +
                '                        <td class="total_ducty_work_hc"></td>\n' +
                '                        <td class="total_over_10_5_time"></td>\n' +
                '                        <td class="total_over_10_5_time_hc"></td>\n' +
                '                        <td class="total_night_work"></td>\n' +
                '                        <td class="total_night_work_hc"></td>\n' +
                '                        <td class="total_travel_abroad"></td>\n' +
                '                        <td class="total_travel_abroad_hc"></td>\n' +
                '                        <td class="total_travel_cn"></td>\n' +
                '                        <td class="total_travel_cn_hc"></td>\n' +
                '                        <td></td>\n' +
                '                        <td class="total_leave_point"></td>\n' +
                '                        <td class="total_dimission_percentage"></td>\n' +
                '                        <td class="total_attendance_percentage"></td>\n' +
                '                        <td class="total_teamloading">teamloading</td>\n' +
                '                        <td class="total_total_percentage">2.92%</td>\n' +
                '                        <td contenteditable="true" class="total_task_force_num"></td>\n' +
                '                        <td style="color: #1986dc;font-weight: 700;" class="total_task_force_point"></td>\n' +
                '                        <td style="width: 150px;background: #f5edac;font-weight: 700;" class="total_all_total">0.00%</td>\n' +
                '                        <td style="width: 150px;background: #fdc0ab;" class="all_total_money">0</td>\n' +
                '                        <td style="display: none;color: #FF9800;font-weight: 700;color: red;">0</td>\n' +
                '                        <td style="display: none;color: #FF9800;font-weight: 700;color: red;">0</td>\n' +
                '                        <td style="display: none;width: 150px;background: #f5edac;font-weight: 700;">0.00%</td>\n' +
                '                        <td style="display: none;width: 150px;background: #fdc0ab;">0</td>\n' +
                '                        <td class="total_violation">0</td>\n' +
                '                        <td class="total_below_quality">0</td>\n' +
                '                        <td style="background: #ffc107;width: 150px;color: red"  class="total_finally_money">0</td>\n' +
                '                    </tr>')

            for(var i = 0;i < department_list.length;i++){
                var data =  response[department_list[i].b_leader];
                $("#table_body_department").append('<tr  class="bonus_reportdepartment">\n' +
                    '                            <td style="background: white" class="department_leader">'+data[1]+'</td>\n' +
                    '                            <td style="background: white;color: red;font-weight: 700;" class="hrdepartment" id="'+data[0]+'_hrdepartment">'+data[3]+'</td>\n' +
                    '                            <td style="background: white"  class="gs_numdepartment" id="'+data[0]+'gsdepartment">'+data[4]+'</td>\n' +
                    '                            <td style="background: white" id="'+data[0]+'gs_weightdepartment">'+data[5]+'</td>\n' +
                    '                            <td class="gs_ratedepartment" id="'+data[0]+'_gs_ratedepartment" style="background: white;color: #DD0CC2;font-weight: 700;">'+data[6]+'</td>\n' +
                    '                            <td class="patent_numdepartment" id="'+data[0]+'patent_numdepartment"  style="background: white" >'+data[7]+'</td>\n' +
                    '                            <td id="'+data[0]+'patent_num_weightdepartment" style="background: white" >'+data[8]+'</td>\n' +
                    '                            <td class="patent_ratedepartment" id="'+data[0]+'_patent_ratedepartment" style="background: white;color: #DD0CC2;font-weight: 700;">'+data[9]+'</td>\n' +
                    '                            <td class="taxdeductiondepartment" id="'+data[0]+'taxdeductiondepartment"  style="background: white" >'+data[10]+'</td>\n' +
                    '                            <td id="'+data[0]+'taxdeduction_weightdepartment" style="background: white" >'+data[11]+'</td>\n' +
                    '                            <td style="background: white;color: #1986dc;font-weight: 700;" class="proposaldepartment" id="'+data[0]+'_proposaldepartment">'+data[12]+'</td>\n' +
                    '                            <td style="display: none;background: white;color: #000000" class="exceed_expecteddepartment" id="'+data[0]+'_exceed_expecteddepartment"  hc="'+data[42]+'">'+data[13]+'</td>\n' +
                    '                            <td style="background: white" id="'+data[0]+'_exceed_expected_pointdepartment" class="exceed_expected_pointdepartment" >'+data[14]+'</td>\n' +
                    '                            <td style="background:white;color: #000000" class="idldepartment" id="'+data[0]+'_idldepartment" >'+data[15]+'</td>\n' +
                    '                            <td class="customerdepartment" id="'+data[0]+'_customerdepartment" style="background: white;color: #1986dc;font-weight: 700;">'+data[16]+'</td>\n' +
                    '                            <td style="background: white" class="duty_workdepartment" id="'+data[0]+'_duty_workdepartment" >'+data[17]+'</td>\n' +
                    '                            <td style="background: white;color: #DD0CC2;font-weight: 700;" class="duty_work_hcdepartment" id="'+data[0]+'_duty_work_hcdepartment">'+data[18]+'</td>\n' +
                    '                            <td style="background: white" class="over_10_5_timedepartment" id="'+data[0]+'_over_10_5_timedepartment" >'+data[19]+'</td>\n' +
                    '                            <td style="background: white;color: #DD0CC2;font-weight: 700;" class="over_10_5_time_hcdepartment" id="'+data[0]+'_over_10_5_time_hcdepartment">'+data[20]+'</td>\n' +
                    '                            <td style="background: white" class="night_workdepartment" id="'+data[0]+'_night_workdepartment" >'+data[21]+'</td>\n' +
                    '                            <td style="background: white;color: #DD0CC2;font-weight: 700;" class="night_work_hcdepartment" id="'+data[0]+'_night_work_hcdepartment">'+data[22]+'</td>\n' +
                    '                            <td style="background: white"  class="travel_abroaddepartment" id="'+data[0]+'_travel_abroaddepartment" >'+data[23]+'</td>\n' +
                    '                            <td style="display: none;background: white;color: #DD0CC2;font-weight: 700;" class="travel_abroad_hcdepartment" id="'+data[0]+'_travel_abroad_hcdepartment" >'+data[24]+'</td>\n' +
                    '                            <td style="background: white"  class="travel_cndepartment" id="'+data[0]+'_travel_cndepartment" >'+data[25]+'</td>\n' +
                    '                            <td style="display: none;background: white;color: #DD0CC2;font-weight: 700;" class="travel_cn_hcdepartment" id="'+data[0]+'_travel_cn_hcdepartment">'+data[26]+'</td>\n' +
                    '                            <td style="background: white" class="leave_prob_department" id="'+data[0]+'_leave_prob_department">'+data[27]+'</td>\n' +
                    '                            <td style="background: white"  class="leave_pointdepartment" id="'+data[0]+'_leave_pointdepartment">'+data[28]+'</td>\n' +
                    '                            <td style="background: white;color: #1986dc;font-weight: 700;" class="dimission_percentagedepartment" id="'+data[0]+'_dimission_percentagedepartment">'+data[29]+'</td>\n' +
                    '                            <td style="background: white;color: #1986dc;font-weight: 700;" class="attendance_percentagedepartment" id="'+data[0]+'_attendance_percentagedepartment">'+data[30]+'</td>\n' +
                    '                            <td style="display: none;background: white;color: #DD0CC2;font-weight: 700;" class="teamloadingdepartment" id="'+data[0]+'_teamloadingdepartment">'+data[39]+'</td>\n' +
                    '                            <td style="background: white" class="total_percentagedepartment" id="'+data[0]+'_total_percentagedepartment">'+data[31]+'</td>\n' +
                    '                            <td  style="background: #cedfef" class="task_force_numdepartment" id="'+data[0]+'_task_force_numdepartment" >'+data[32]+'</td>\n' +
                    '                            <td style="background: white" style="color: #1986dc;font-weight: 700;" class="task_force_pointdepartment" id="'+data[0]+'_task_force_pointdepartment">'+data[33]+'</td>\n' +
                    '                            <td  style="width: 150px;background:  white;" class="all_totaldepartment" id="'+data[0]+'_all_totaldepartment">'+data[34]+'</td>\n' +
                    '                            <td  style="width: 150px;background:  white;"  id="'+data[0]+'_all_total_moneydepartment">'+data[35]+'</td>\n' +
                    '                            <td style="display: none;background: white;color: #252422;font-weight: 700;">0</td>\n' +
                    '                            <td style="display: none;background: white;color: #252422;font-weight: 700;">'+data[41]+'</td>\n' +
                    '                            <td style="display: none;width: 150px;background: white;" class="change_percentage" id="'+data[0]+'_change_percentage">'+data[40]+'</td>\n' +
                    '                            <td style="display: none;width: 150px;background: white;" id="'+data[0]+'_last_year_money">'+data[41]+'</td>\n' +
                    '                            <td contenteditable="true" style="background: white;" class="violationdepartment" id="'+data[0]+'_violationdepartment">'+data[36]+'</td>\n' +
                    '                            <td contenteditable="true" style="background: white;" class="below_qualitydepartment" id="'+data[0]+'_below_qualitydepartment">'+data[37]+'</td>\n' +
                    '                            <td style="background: white;width: 150px" class="finally_moneydepartment" id="'+data[0]+'_finally_moneydepartment">'+data[38]+'</td>\n' +
                    '                        </tr>')
            };
            $("#table_body_department").append('<tr style="font-size: 15px;font-weight: 700;" class="bonus_reportdepartment">\n' +
                '                        <td style="background: floralwhite;color: darkred;font-size: 16px;">EERF Total</td>\n' +
                '                        <td style="background: floralwhite;color: white;font-weight: 700;"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_gs_numdepartment"></td>\n' +
                '                        <td style="background: floralwhite;"class="total_gs_weightdepartment"></td>\n' +
                '                        <td style="background: floralwhite;"></td>\n' +
                '                        <td style="background: floralwhite;"class="total_patent_numdepartment"></td>\n' +
                '                        <td style="background: floralwhite;"class="total_patent_weightdepartment"></td>\n' +
                '                        <td style="background: floralwhite;"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_taxdeduction_numdepartment"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_taxdeduction_weightdepartment"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_proposal_percentagedepartment"></td>\n' +
                '                        <td style="display: none;background: floralwhite;" class="total_exceed_expecteddepartment"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_exceed_expected_pointdepartment"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_idldepartment"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_customerdepartment"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_duty_workdepartment"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_duty_workdepartment_hc"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_over_10_5_timedepartment"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_over_10_5_timedepartment_hc"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_night_workdepartment"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_night_workdepartment_hc"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_travel_abroaddepartment"></td>\n' +
                '                        <td style="display: none;background: floralwhite;" class="total_travel_abroaddepartment_hc"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_travel_cndepartment"></td>\n' +
                '                        <td style="display: none;background: floralwhite;" class="total_travel_cndepartment_hc"></td>\n' +
                '                        <td style="background: floralwhite;" ></td>\n' +
                '                        <td style="background: floralwhite;" class="total_leave_pointdepartment"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_dimission_percentagedepartment"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_attendance_percentagedepartment"></td>\n' +
                '                        <td style="display: none;background: floralwhite;" class="total_teamloadingdepartment"></td>\n' +
                '                        <td style="background: floralwhite;" class="total_total_percentagedepartment"></td>\n' +
                '                        <td style="background: floralwhite;"  contenteditable="true" class="total_task_force_numdepartment"></td>\n' +
                '                        <td style="background: floralwhite;color: #1986dc;font-weight: 700;" class="total_task_force_pointdepartment"></td>\n' +
                '                        <td style="background: floralwhite;width: 150px;background: #f5edac;font-weight: 700;" class="total_all_totaldepartment"></td>\n' +
                '                        <td style="background: floralwhite;width: 150px;background: #fdc0ab;" class="all_total_moneydepartment"></td>\n' +
                '                        <td style="display: none;background: floralwhite;color: #FF9800;font-weight: 700;color: red;">0</td>\n' +
                '                        <td style="display: none;background: floralwhite;color: #FF9800;font-weight: 700;color: red;">0</td>\n' +
                '                        <td style="display: none;background: floralwhite;width: 150px;background: #f5edac;font-weight: 700;"></td>\n' +
                '                        <td style="display: none;background: floralwhite;width: 150px;background: #fdc0ab;">0</td>\n' +
                '                        <td style="background: floralwhite;" class="total_violationdepartment">0</td>\n' +
                '                        <td style="background: floralwhite;" class="total_below_qualitydepartment">0</td>\n' +
                '                        <td style="background: floralwhite;width: 150px;color: red"  class="total_finally_moneydepartment">0</td>\n' +
                '                    </tr>');
            // $("#table_score").FrozenTable(0, 1, 1);

            $("#ipt_z").val(response.bp_totalmoney);
            $("#ipt_zjj").val(response.bp_personalmoney);
            $("#ipt_td").val(response.bp_teammoney);
            $("#ipt_qt").val(response.bp_othermoney);

            $("#gs_weight").html(response.bp_gsweight_t);
            $("#patent_weight").html(response.bp_patentweight_t);
            $("#taxdeduction_weight").html(response.bp_taxweight_t);
            $("#gs_weightdepartment").html(response.bp_gsweight_d);
            $("#patent_weightdepartment").html(response.bp_patentweight_d);
            $("#taxdeduction_weightdepartment").html(response.bp_taxweight_d);

            $("#hr_percentagedepartment").html(response.bp_hrper_d);
            $("#percentage_1department").html(response.bp_otherper_d);
            $("#task_force_percentagedepartment").html(response.bp_taskforceper_d);
            $("#percentage_1").html(response.bp_otherper_t);
            $("#task_force_percentage").html(response.bp_taskforceper_t);
            $("#proposal_percentage").html(response.bp_proposal_t);
            $("#exceed_expected_percentage").html(response.bp_ee_t);
            $("#idl_percentage").html(response.bp_idl_t);
            $("#duty_work_percentage").html(response.bp_duty_t);
            $("#over_10_5_time_percentage").html(response.bp_10_5_t);
            $("#night_work_percentage").html(response.bp_night_t);
            $("#travel_abroad_percentage").html(response.bp_travel_abroad_t);
            $("#travel_cn_percentage").html(response.bp_travel_cn_t);
            $("#leave_percentage").html(response.bp_leave_t);

            $("#proposal_percentagedepartment").html(response.bp_proposal_d);
            $("#exceed_expected_percentagedepartment").html(response.bp_ee_d);
            $("#idl_percentagedepartment").html(response.bp_idl_d);
            $("#duty_work_percentagedepartment").html(response.bp_duty_d);
            $("#over_10_5_time_percentagedepartment").html(response.bp_10_5_d);
            $("#night_work_percentagedepartment").html(response.bp_night_d);
            $("#travel_abroad_percentagedepartment").html(response.bp_travel_abroad_d);
            $("#travel_cn_percentagedepartment").html(response.bp_travel_cn_d);
            $("#leave_percentagedepartment").html(response.bp_leave_d);
            alert("讀取成功");
            sum_team();
            color_check();


        },
        error: function () {
            alert("Error");
        }
    });
    } else {
        alert("請選擇且僅選擇一條記錄并點擊讀取")
    }
});


// $("#team_data").click(function () {
//
// });

function sum_team(if_focus) {
    // 判断当前显示科级还是部级
    setTimeout(function () {
        if($('#table_score_team').css('display') == 'none'){
             // 部级
        var team_total = (parseFloat($('#hr_percentagedepartment').html())+parseFloat($('#proposal_percentagedepartment').html())*((parseFloat($('#percentage_1department').html()))/100))+((parseFloat($('#exceed_expected_percentagedepartment').html()) + parseFloat($('#idl_percentagedepartment').html()))*((parseFloat($('#percentage_1department').html()))/100))+((parseFloat($('#duty_work_percentagedepartment').html()) + parseFloat($('#over_10_5_time_percentagedepartment').html())+ parseFloat($('#night_work_percentagedepartment').html())+ parseFloat($('#travel_abroad_percentagedepartment').html())+parseFloat($('#travel_cn_percentagedepartment').html())+parseFloat($('#leave_percentagedepartment').html()))*((parseFloat($('#percentage_1department').html()))/100))+(parseFloat($('#task_force_percentagedepartment').html()));
        $('.top_left_1').val(($('#proposal_percentagedepartment').html())+'*'+($('#percentage_1department').html()));
        $('.top_left_2').val((parseFloat($('#exceed_expected_percentagedepartment').html()) + parseFloat($('#idl_percentagedepartment').html()))+'%*'+($('#percentage_1department').html()));
        $('.top_left_3').val((parseFloat($('#duty_work_percentagedepartment').html()) + parseFloat($('#over_10_5_time_percentagedepartment').html())+ parseFloat($('#night_work_percentagedepartment').html())+ parseFloat($('#travel_abroad_percentagedepartment').html())+parseFloat($('#travel_cn_percentagedepartment').html())+parseFloat($('#leave_percentagedepartment').html()))+'*'+($('#percentage_1department').html()));
        $('.top_left_4').val(($('#task_force_percentagedepartment').html()));
        $('.top_left_5').val($('#hr_percentagedepartment').html());
        $('.top_left_0').val(team_total+"%");

     }else if($('#table_score_department').css('display') == 'none'){
        // 課級
        var department_total = (parseFloat($('#proposal_percentage').html())*((parseFloat($('#percentage_1').html()))/100))+((parseFloat($('#exceed_expected_percentage').html()) + parseFloat($('#idl_percentage').html()))*((parseFloat($('#percentage_1').html()))/100))+((parseFloat($('#duty_work_percentage').html()) + parseFloat($('#over_10_5_time_percentage').html())+ parseFloat($('#night_work_percentage').html())+ parseFloat($('#travel_abroad_percentage').html())+parseFloat($('#travel_cn_percentage').html())+parseFloat($('#leave_percentage').html()))*((parseFloat($('#percentage_1').html()))/100))+(parseFloat($('#task_force_percentage').html()));

        $('.top_left_1').val(($('#proposal_percentage').html())+'*'+($('#percentage_1').html()));
        $('.top_left_2').val((parseFloat($('#exceed_expected_percentage').html()) + parseFloat($('#idl_percentage').html()))+'%*'+($('#percentage_1').html()));
        $('.top_left_3').val((parseFloat($('#duty_work_percentage').html()) + parseFloat($('#over_10_5_time_percentage').html())+ parseFloat($('#night_work_percentage').html())+ parseFloat($('#travel_abroad_percentage').html())+parseFloat($('#travel_cn_percentage').html())+parseFloat($('#leave_percentage').html()))+'%*'+($('#percentage_1').html()));
        $('.top_left_4').val($('#task_force_percentage').html());
        $('.top_left_0').val(department_total+"%")
     }
    },200);

    if(isclick){
        isclick= false;
        //下面添加需要执行的事件
        if(!input_check()){
            return;
        }
    }
     //定时器
    setTimeout(function(){
         isclick = true;
     }, 1000);
    if(if_focus){
        return
    }
    percentage_check_2();
    var total_gs = 0.0;
    var total_gs_weight = 0.0;
    var gs_weight = parseFloat($("#gs_weight").html());
    $(".gs_num").each(function () {
        var gs_num = parseFloat($(this).html());
        var gs_num_weight = gs_num * gs_weight;
        total_gs_weight = total_gs_weight + gs_num_weight;
        $("#"+$(this).attr('id')+"_weight").html(gs_num_weight.toFixed(3));
        total_gs = total_gs + gs_num;
    });
    $(".total_gs_num").each(function () {
        $(this).html(total_gs);
    });
    $(".total_gs_weight").each(function () {
        $(this).html(total_gs_weight.toFixed(3));
    });

    var total_patent_weight = 0.0;
    var total_patent_num = 0.0;
    var patent_weight = parseFloat($("#patent_weight").html());
    $(".patent_num").each(function () {
        var patent_num = parseFloat($(this).html());
        total_patent_num = total_patent_num + patent_num;
        var patent_num_weight = patent_num * patent_weight;
        $("#"+$(this).attr('id')+"_weight").html(patent_num_weight.toFixed(3));
        total_patent_weight = total_patent_weight + patent_num_weight
    });
    $('.total_patent_num').each(function () {
        $(this).html(total_patent_num);
    });
    $('.total_patent_weight').each(function () {
        $(this).html(total_patent_weight.toFixed(3));
    });

    var total_taxdeduction = 0.0;
    var taxdeduction_weight = parseFloat($("#taxdeduction_weight").html());
    var total_taxdeduction_weight = 0.0;
    $('.taxdeduction').each(function () {
        var taxdeduction_num =  parseFloat($(this).html());
        total_taxdeduction = total_taxdeduction + taxdeduction_num;
        var taxdeduction_num_weight = taxdeduction_num * taxdeduction_weight;
        $("#"+$(this).attr('id')+"_weight").html(taxdeduction_num_weight.toFixed(3));
        total_taxdeduction_weight = total_taxdeduction_weight + taxdeduction_num_weight;
    });
    $(".total_taxdeduction_num").each(function () {
        $(this).html(total_taxdeduction)
    });
    $(".total_taxdeduction_weight").each(function () {
        $(this).html(total_taxdeduction_weight.toFixed(3))
    });


    var proposal_percentage = parseFloat($("#proposal_percentage").html().split("%")[0]);
    var total_proposal_percentage = 0.0;
    var total_proposal_point = parseFloat($(".total_gs_weight").html()) + parseFloat($(".total_patent_weight").html()) + parseFloat($(".total_taxdeduction_weight").html());
    $(".proposal").each(function () {
        var team_id = $(this).attr("id").split("_")[0];
        var gs_weight = parseFloat($("#"+team_id+"gs_weight").html());
        var patent_num_weight = parseFloat($("#"+team_id+"patent_num_weight").html());
        var taxdeduction_weight = parseFloat($("#"+team_id+"taxdeduction_weight").html());
        var proposal_point = ((gs_weight + patent_num_weight + taxdeduction_weight)/total_proposal_point) * proposal_percentage ;
        total_proposal_percentage = total_proposal_percentage + proposal_point;
        $(this).html(proposal_point.toFixed(3) + "%")
    });
    $(".total_proposal_percentage").each(function () {
        $(this).html(total_proposal_percentage.toFixed(3) + "%")
    });

    var total_exceed_expected = 0.0;
    var total_exceed_expected_point = 0.0;
    var team_num = 0.0;
    $(".exceed_expected").each(function () {
        team_num = team_num + 1;
        var exceed_expected = parseFloat($(this).html());
        total_exceed_expected = total_exceed_expected + exceed_expected;

    });
    color_check_2("exceed_expected",total_exceed_expected/team_num);
    $(".exceed_expected_point").each(function () {
        var exceed_expected_point = parseFloat($(this).html());
        total_exceed_expected_point = total_exceed_expected_point + exceed_expected_point;
    });
    $(".total_exceed_expected").each(function () {
        $(this).html(total_exceed_expected.toFixed(3));
    });
    $(".total_exceed_expected_point").each(function () {
        $(this).html(total_exceed_expected_point.toFixed(3));
    });

    var total_idl = 0.00;
    $(".idl").each(function () {
       var idl = parseFloat($(this).html() );
       total_idl = total_idl + idl;
    });
    $(".total_idl").each(function () {
        $(this).html(total_idl.toFixed(3));
    });

    var total_customer_percentage = 0.00;
    var exceed_expected_percentage = parseFloat($("#exceed_expected_percentage").html().split("%")[0]);
    var idl_percentage = parseFloat($("#idl_percentage").html().split("%"));
    $(".customer").each(function () {
        var team_id = $(this).attr("id").split("_")[0];
        var exceed_expected_point = parseFloat($("#" + team_id +"_exceed_expected_point").html());
        var idl = parseFloat($("#" + team_id +"_idl").html());
        var customer_percentage = ((exceed_expected_point/total_exceed_expected_point)*exceed_expected_percentage) + ((idl/total_idl)*idl_percentage);
        $(this).html((customer_percentage.toFixed(3))+"%");
        total_customer_percentage = total_customer_percentage +customer_percentage;
    });
    $(".total_customer").each(function () {
       $(this).html(total_customer_percentage.toFixed(3) + "%")
    });

    var total_duty_work = 0.0;
    $(".duty_work").each(function () {
        var duty_work = parseFloat($(this).html());
        total_duty_work = total_duty_work +duty_work
    });
    $(".total_duty_work").each(function () {
        $(this).html(total_duty_work.toFixed(3))
    });

    var total_over_10_5_time = 0.0;
    $(".over_10_5_time").each(function () {
        var over_10_5_time = parseFloat($(this).html());
        total_over_10_5_time = total_over_10_5_time +over_10_5_time;
    });
    $(".total_over_10_5_time").each(function () {
        $(this).html(total_over_10_5_time.toFixed(3))
    });

    var total_night_work = 0.0;
    $(".night_work").each(function () {
        var night_work = parseFloat($(this).html());
        total_night_work = total_night_work + night_work;
    });
    $(".total_night_work").each(function () {
        $(this).html(total_night_work.toFixed(3));
    });

    var total_travel_abroad = 0.0;
    $(".travel_abroad").each(function () {
        var travel_abroad = parseFloat($(this).html());
        total_travel_abroad = total_travel_abroad + travel_abroad;
    });
    $(".total_travel_abroad").each(function () {
        $(this).html(total_travel_abroad.toFixed(3));
    });

    var total_travel_cn = 0.0;
    $(".travel_cn").each(function () {
        var travel_cn = parseFloat($(this).html());
        total_travel_cn = total_travel_cn + travel_cn;
    });
    $(".total_travel_cn").each(function () {
        $(this).html(total_travel_cn.toFixed(3));
    });

    var total_leave_point = 0.0
    $(".leave_point").each(function () {
        var leave_point = parseFloat($(this).html());
        total_leave_point = total_leave_point + leave_point;
    });
    $(".total_leave_point").each(function () {
        $(this).html(total_leave_point.toFixed(3));
    });

    var dimission_percentage = parseFloat($("#leave_percentage").html().split("%")[0]);
    var total_dimission_percentage = 0.0;
    $(".dimission_percentage").each(function () {
        var team_id = $(this).attr('id').split("_")[0];
        var leave_point = parseFloat($("#" + team_id + "_leave_point").html());
        var percentage = (leave_point/total_leave_point)*dimission_percentage;
        total_dimission_percentage = total_dimission_percentage + percentage;
        $(this).html(percentage.toFixed(3) + "%");
    });
    $(".total_dimission_percentage").each(function () {
        $(this).html(total_dimission_percentage.toFixed(3) + "%")
    });

    var duty_work_percentage = parseFloat($("#duty_work_percentage").html());
    var over_10_5_time_percentage = parseFloat($("#over_10_5_time_percentage").html());
    var night_work_percentage = parseFloat($("#night_work_percentage").html());
    var travel_abroad_percentage = parseFloat($("#travel_abroad_percentage").html());
    var travel_cn_percentage = parseFloat($("#travel_cn_percentage").html());
    var total_attendance_percentage = 0.0;
    var total_percentage = 0.0;
    var percentage_1 = parseFloat($("#percentage_1").html().split("%")[0]);
    $(".attendance_percentage").each(function () {
        var team_id = $(this).attr('id').split("_")[0];
        var attendance_percentage = parseFloat($("#" + team_id +"_dimission_percentage").html().split("%")[0]) + ((parseFloat($("#" + team_id +"_duty_work").html())/total_duty_work)*duty_work_percentage)+ ((parseFloat($("#" + team_id +"_over_10_5_time").html())/total_over_10_5_time) * over_10_5_time_percentage) + ((parseFloat($("#" + team_id +"_night_work").html())/total_night_work)*night_work_percentage) +((parseFloat($("#" + team_id +"_travel_abroad").html())/total_travel_abroad)*travel_abroad_percentage) + ((parseFloat($("#" + team_id +"_travel_cn").html())/total_travel_cn)*travel_cn_percentage);
        total_attendance_percentage = total_attendance_percentage + attendance_percentage;
        var team_proposal = parseFloat($("#" + team_id +"_proposal").html().split("%")[0]);
        var team_cust = parseFloat($("#" + team_id +"_customer").html().split("%")[0]);
        total_percentage = total_percentage + ((attendance_percentage + team_proposal + team_cust)*(percentage_1/100));
        $("#" + team_id + "_total_percentage").html(((attendance_percentage + team_proposal + team_cust)*(percentage_1/100)).toFixed(3) + "%");
        $(this).html(attendance_percentage.toFixed(3) + "%")
    });
    $(".total_attendance_percentage").each(function () {
        $(this).html(total_attendance_percentage.toFixed(3) + "%");
    });
    $(".total_total_percentage").each(function () {
        $(this).html(total_percentage.toFixed(3) + "%");
    });

    var task_force_percentage = parseFloat($("#task_force_percentage").html().split("%")[0]);
    var total_task_force_num = 0.0;
    var total_task_force_point = 0.0;
    $(".task_force_num").each(function () {
        var task_force_num = parseFloat($(this).html());
        total_task_force_num = total_task_force_num + task_force_num;
    });
    $(".task_force_point").each(function () {
        var team_id = $(this).attr('id').split("_")[0];
        var task_force_point = (parseFloat($("#" + team_id + "_task_force_num").html()) / total_task_force_num) * task_force_percentage;
        $(this).html(task_force_point.toFixed(3) + "%");
        total_task_force_point = total_task_force_point + task_force_point;
    });
    $(".total_task_force_point").each(function () {
        $(this).html(total_task_force_point.toFixed(3) + "%");
    });
    $(".total_task_force_num").each(function () {
        $(this).html(total_task_force_num.toFixed(3));
    });

    var total_all_total = 0.0;
    var money  = parseFloat($("#ipt_zjj").val());
    var all_total_money = 0.0;
    $(".all_total").each(function () {
        var team_id = $(this).attr("id").split("_")[0];
        var all_total = parseFloat($("#" + team_id + "_total_percentage").html().split("%")[0]) + parseFloat($("#" + team_id + "_task_force_point").html().split("%")[0]);
        total_all_total  = total_all_total + all_total;
        var total_money = money*all_total/100.0;
        all_total_money = all_total_money + total_money;
        $("#"+team_id+"_all_total_money" ).html(total_money.toFixed(3));
        $("#"+team_id+"_all_total_money" ).next().html(total_money.toFixed(3))
        $(this).html(all_total.toFixed(3) + '%')

    });
    $(".total_all_total").each(function () {
        $(this).html(total_all_total.toFixed(3) + "%")
    });
    $(".all_total_money").each(function () {
        $(this).html(all_total_money.toFixed(3))
        $(this).next().html(all_total_money.toFixed(3))
    });


    var total_violation = 0.0;
    var total_below_quality = 0.0;
    var total_finally_money = 0.0;
    $(".finally_money").each(function () {
        var team_id = $(this).attr("id").split("_")[0];
        var violation = parseFloat($("#"+team_id+"_violation").html());
        var below_quality = parseFloat($("#"+team_id+"_below_quality").html());
        var money = parseFloat($("#"+team_id+"_all_total_money").html());
        var finally_money = money - violation - below_quality;
        total_below_quality = total_below_quality + below_quality;
        total_violation = total_violation + violation;
        total_finally_money = total_finally_money + finally_money;
        $(this).html(finally_money.toFixed(3))
    });
    $(".total_violation").each(function () {
        $(this).html(total_violation.toFixed(3));
    });
    $(".total_below_quality").each(function () {
        $(this).html(total_below_quality.toFixed(3));
    });
    $(".total_finally_money").each(function () {
        $(this).html(total_finally_money.toFixed(3));
    });


    var total_duty_work_hc = 0.0;

    $('.duty_work_hc').each(function () {

        var duty_work_hc = parseFloat($(this).html());
        total_duty_work_hc = total_duty_work_hc + duty_work_hc;
    });
    $('.total_ducty_work_hc').each(function () {
        $(this).html(total_duty_work_hc.toFixed(3))
    });
    color_check_2("duty_work_hc",total_duty_work_hc/team_num);


    var total_over_10_5_time_hc = 0.0;
    $('.over_10_5_time_hc').each(function () {
        var over_10_5_time_hc = parseFloat($(this).html());
        total_over_10_5_time_hc = total_over_10_5_time_hc + over_10_5_time_hc;
    });
    $(".total_over_10_5_time_hc").each(function () {
       $(this).html(total_over_10_5_time_hc.toFixed(3));
    });
    color_check_2("over_10_5_time_hc",total_over_10_5_time_hc/team_num);


    var total_night_work_hc = 0.0;
    $('.night_work_hc').each(function () {
        var night_work_hc = parseFloat($(this).html());
        total_night_work_hc = total_night_work_hc + night_work_hc;
    });
    $(".total_night_work_hc").each(function () {
       $(this).html(total_night_work_hc.toFixed(3));
    });
    color_check_2("night_work_hc",total_night_work_hc/team_num);


    var total_travel_abroad_hc = 0.0;
    $('.travel_abroad_hc').each(function () {
        var travel_abroad_hc = parseFloat($(this).html());
        total_travel_abroad_hc = total_travel_abroad_hc + travel_abroad_hc;
    });
    $(".total_travel_abroad_hc").each(function () {
       $(this).html(total_travel_abroad_hc.toFixed(3));
    });
    color_check_2("travel_abroad_hc",total_travel_abroad_hc/team_num);


    var total_travel_cn_hc = 0.0;
    $('.travel_cn_hc').each(function () {
        var travel_cn_hc = parseFloat($(this).html());
        total_travel_cn_hc = total_travel_cn_hc + travel_cn_hc;
    });
    $(".total_travel_cn_hc").each(function () {
       $(this).html(total_travel_cn_hc.toFixed(3));
    });
    color_check_2("travel_cn_hc", total_travel_cn_hc/team_num);



    var total_teamloading = 0.0
    $('.teamloading').each(function () {
        var team_id = $(this).attr("id").split("_")[0];

        var duty_work_hc = parseFloat($("#"+ team_id +"_duty_work_hc").html());


        var over_10_5_time_hc = parseFloat($("#"+ team_id +"_over_10_5_time_hc").html());
        var night_work_hc= parseFloat($("#"+ team_id +"_night_work_hc").html());
        var travel_abroad_hc= parseFloat($("#"+ team_id +"_travel_abroad_hc").html());
        var travel_cn_hc= parseFloat($("#"+ team_id +"_travel_cn_hc").html());

        var result = ((duty_work_hc/total_duty_work_hc)*duty_work_percentage + (over_10_5_time_hc/total_over_10_5_time_hc)*over_10_5_time_percentage + (night_work_hc/total_night_work_hc)*night_work_percentage + (travel_abroad_hc/total_travel_abroad_hc)*travel_abroad_percentage + (travel_cn_hc/total_travel_cn_hc)*travel_cn_percentage) * 100/(duty_work_percentage+over_10_5_time_percentage+night_work_percentage+travel_abroad_percentage+travel_cn_percentage)
        total_teamloading = total_teamloading + result;
        $(this).html(result.toFixed(3) + "%")
    });
    $(".total_teamloading").each(function () {
        $(this).html(total_teamloading.toFixed(3) + "%")
    });
    color_check_2("teamloading", total_teamloading/team_num);


    sum_department();

}







function sum_department() {
    var total_gs = 0.0;
    var total_gs_weight = 0.0;
    var gs_weight = parseFloat($("#gs_weightdepartment").html());
    $(".gs_numdepartment").each(function () {
        var gs_num = parseFloat($(this).html());
        var gs_num_weight = gs_num * gs_weight;
        total_gs_weight = total_gs_weight + gs_num_weight;
        $("#"+ $(this).attr('id').split("department")[0] +"_weightdepartment").html(gs_num_weight.toFixed(3));
        total_gs = total_gs + gs_num;
    });
    $(".total_gs_numdepartment").each(function () {
        $(this).html(total_gs);
    });
    $(".total_gs_weightdepartment").each(function () {
        $(this).html(total_gs_weight.toFixed(3));
    });

    var hr_total = 0.0;

    $(".hrdepartment").each(function () {
        hr_total = hr_total + parseFloat($(this).html().split("%")[0])
    });

    $('.total_hrdepartment').each(function () {
        $(this).html(hr_total.toFixed(3)+"%")
    });





    var total_patent_weight = 0.0;
    var total_patent_num = 0.0;
    var patent_weight = parseFloat($("#patent_weightdepartment").html());
    $(".patent_numdepartment").each(function () {
        var patent_num = parseFloat($(this).html());
        total_patent_num = total_patent_num + patent_num;
        var patent_num_weight = patent_num * patent_weight;
        $("#"+ $(this).attr('id').split("department")[0] + "_weightdepartment").html(patent_num_weight.toFixed(3));
        total_patent_weight = total_patent_weight + patent_num_weight
    });
    $('.total_patent_numdepartment').each(function () {
        $(this).html(total_patent_num);
    });
    $('.total_patent_weightdepartment').each(function () {
        $(this).html(total_patent_weight.toFixed(3));
    });

    var total_taxdeduction = 0.0;
    var taxdeduction_weight = parseFloat($("#taxdeduction_weightdepartment").html());
    var total_taxdeduction_weight = 0.0;
    $('.taxdeductiondepartment').each(function () {
        var taxdeduction_num =  parseFloat($(this).html());
        total_taxdeduction = total_taxdeduction + taxdeduction_num;
        var taxdeduction_num_weight = taxdeduction_num * taxdeduction_weight;
        $("#" + $(this).attr('id').split("department")[0] + "_weightdepartment").html(taxdeduction_num_weight.toFixed(3));
        total_taxdeduction_weight = total_taxdeduction_weight + taxdeduction_num_weight;
    });
    $(".total_taxdeduction_numdepartment").each(function () {
        $(this).html(total_taxdeduction)
    });
    $(".total_taxdeduction_weightdepartment").each(function () {
        $(this).html(total_taxdeduction_weight.toFixed(3))
    });


    var proposal_percentage = parseFloat($("#proposal_percentagedepartment").html().split("%")[0]);
    var total_proposal_percentage = 0.0;
    var total_proposal_point = parseFloat($(".total_gs_weightdepartment").html()) + parseFloat($(".total_patent_weightdepartment").html()) + parseFloat($(".total_taxdeduction_weightdepartment").html());
    $(".proposaldepartment").each(function () {
        var team_id = $(this).attr("id").split("_")[0];
        var gs_weight = parseFloat($("#"+team_id+"gs_weightdepartment").html());
        var patent_num_weight = parseFloat($("#"+team_id+"patent_num_weightdepartment").html());
        var taxdeduction_weight = parseFloat($("#"+team_id+"taxdeduction_weightdepartment").html());
        var proposal_point = ((gs_weight + patent_num_weight + taxdeduction_weight)/total_proposal_point) * proposal_percentage ;
        total_proposal_percentage = total_proposal_percentage + proposal_point;
        $(this).html(proposal_point.toFixed(3) + "%")
    });
    $(".total_proposal_percentagedepartment").each(function () {
        $(this).html(total_proposal_percentage.toFixed(3) + "%")
    });

    // var total_exceed_expected = 0.0;
    var total_exceed_expected_point = 0.0
    // $(".exceed_expecteddepartment").each(function () {
    //
    //     var exceed_expected = parseFloat($(this).html());
    //     total_exceed_expected = total_exceed_expected + exceed_expected;
    //
    // });
    $(".exceed_expected_pointdepartment").each(function () {
        var exceed_expected_point = parseFloat($(this).html());
        total_exceed_expected_point = total_exceed_expected_point + exceed_expected_point;
    })
    // $(".total_exceed_expecteddepartment").each(function () {
    //     $(this).html(total_exceed_expected.toFixed(3));
    // });
    $(".total_exceed_expected_pointdepartment").each(function () {
        $(this).html(total_exceed_expected_point.toFixed(3));
    });

    var total_idl = 0.00;
    $(".idldepartment").each(function () {
       var idl = parseFloat($(this).html() );
       total_idl = total_idl + idl;
    });
    $(".total_idldepartment").each(function () {
        $(this).html(total_idl.toFixed(3));
    });

    var total_customer_percentage = 0.00;
    var exceed_expected_percentage = parseFloat($("#exceed_expected_percentagedepartment").html().split("%")[0]);
    var idl_percentage = parseFloat($("#idl_percentagedepartment").html().split("%"));
    $(".customerdepartment").each(function () {
        var team_id = $(this).attr("id").split("_")[0];
        var exceed_expected_pointdepartment = parseFloat($("#" + team_id +"_exceed_expected_pointdepartment").html());
        var idl = parseFloat($("#" + team_id +"_idldepartment").html());
        var customer_percentage = ((exceed_expected_pointdepartment/total_exceed_expected_point)*exceed_expected_percentage) + ((idl/total_idl)*idl_percentage);
        $(this).html((customer_percentage.toFixed(3))+"%");
        total_customer_percentage = total_customer_percentage +customer_percentage;
    });
    $(".total_customerdepartment").each(function () {
       $(this).html(total_customer_percentage.toFixed(3) + "%")
    });

    var total_duty_work = 0.0;
    $(".duty_workdepartment").each(function () {
        var duty_work = parseFloat($(this).html());
        total_duty_work = total_duty_work +duty_work
    });
    $(".total_duty_workdepartment").each(function () {
        $(this).html(total_duty_work.toFixed(3))
    });

    var total_over_10_5_time = 0.0;
    $(".over_10_5_timedepartment").each(function () {
        var over_10_5_time = parseFloat($(this).html());
        total_over_10_5_time = total_over_10_5_time +over_10_5_time;
    });
    $(".total_over_10_5_timedepartment").each(function () {
        $(this).html(total_over_10_5_time.toFixed(3))
    });

    var total_night_work = 0.0;
    $(".night_workdepartment").each(function () {
        var night_work = parseFloat($(this).html());
        total_night_work = total_night_work + night_work;
    });
    $(".total_night_workdepartment").each(function () {
        $(this).html(total_night_work.toFixed(3));
    });

    var total_travel_abroad = 0.0;
    $(".travel_abroaddepartment").each(function () {
        var travel_abroad = parseFloat($(this).html());
        total_travel_abroad = total_travel_abroad + travel_abroad;
    });
    $(".total_travel_abroaddepartment").each(function () {
        $(this).html(total_travel_abroad.toFixed(3));
    });

    var total_travel_cn = 0.0;
    $(".travel_cndepartment").each(function () {
        var travel_cn = parseFloat($(this).html());
        total_travel_cn = total_travel_cn + travel_cn;
    });
    $(".total_travel_cndepartment").each(function () {
        $(this).html(total_travel_cn.toFixed(3));
    });
    var leave_prob_max = 0.0;
    $(".leave_prob_department").each(function () {
        var this_leave_prob = parseFloat($(this).html().split("%")[0]);
        if (this_leave_prob > leave_prob_max){
            leave_prob_max = this_leave_prob;
        }
    });
    $(".leave_prob_department").each(function () {
        var team_id = $(this).attr('id').split("_")[0];
        var this_leave_prob = parseFloat($(this).html().split("%")[0]);

        if ($(this).attr('hc')) {
            var hc = parseFloat($(this).attr('hc'));
            $("#"+team_id+"_leave_pointdepartment").html(((leave_prob_max - this_leave_prob)*hc/100).toFixed(3));
        }

    });



    var total_leave_point = 0.0
    $(".leave_pointdepartment").each(function () {
        var leave_point = parseFloat($(this).html());
        total_leave_point = total_leave_point + leave_point;
    });
    $(".total_leave_pointdepartment").each(function () {
        $(this).html(total_leave_point.toFixed(3));
    });

    var dimission_percentage = parseFloat($("#leave_percentagedepartment").html().split("%")[0]);
    var total_dimission_percentage = 0.0;
    $(".dimission_percentagedepartment").each(function () {
        var team_id = $(this).attr('id').split("_")[0];
        var leave_point = parseFloat($("#" + team_id + "_leave_pointdepartment").html());
        var percentage = (leave_point/total_leave_point)*dimission_percentage;
        total_dimission_percentage = total_dimission_percentage + percentage;
        $(this).html(percentage.toFixed(3) + "%");
    });
    $(".total_dimission_percentagedepartment").each(function () {
        $(this).html(total_dimission_percentage.toFixed(3) + "%")
    });

    var duty_work_percentage = parseFloat($("#duty_work_percentagedepartment").html());
    var over_10_5_time_percentage = parseFloat($("#over_10_5_time_percentagedepartment").html());
    var night_work_percentage = parseFloat($("#night_work_percentagedepartment").html());
    var travel_abroad_percentage = parseFloat($("#travel_abroad_percentagedepartment").html());
    var travel_cn_percentage = parseFloat($("#travel_cn_percentagedepartment").html());
    var total_attendance_percentage = 0.0;
    var total_percentage = 0.0;
    var percentage_1 = parseFloat($("#percentage_1department").html().split("%")[0]);
    $(".attendance_percentagedepartment").each(function () {
        var team_id = $(this).attr('id').split("_")[0];
        var attendance_percentage = parseFloat($("#" + team_id +"_dimission_percentagedepartment").html().split("%")[0]) + ((parseFloat($("#" + team_id +"_duty_workdepartment").html())/total_duty_work)*duty_work_percentage)+ ((parseFloat($("#" + team_id +"_over_10_5_timedepartment").html())/total_over_10_5_time) * over_10_5_time_percentage) + ((parseFloat($("#" + team_id +"_night_workdepartment").html())/total_night_work)*night_work_percentage) +((parseFloat($("#" + team_id +"_travel_abroaddepartment").html())/total_travel_abroad)*travel_abroad_percentage) + ((parseFloat($("#" + team_id +"_travel_cndepartment").html())/total_travel_cn)*travel_cn_percentage);
        total_attendance_percentage = total_attendance_percentage + attendance_percentage;
        var team_proposal = parseFloat($("#" + team_id +"_proposaldepartment").html().split("%")[0]);
        var team_cust = parseFloat($("#" + team_id +"_customerdepartment").html().split("%")[0]);
        total_percentage = total_percentage + ((attendance_percentage + team_proposal + team_cust)*(percentage_1/100));
        $("#" + team_id + "_total_percentagedepartment").html(((attendance_percentage + team_proposal + team_cust)*(percentage_1/100)).toFixed(3) + "%");
        $(this).html(attendance_percentage.toFixed(3) + "%")
    });
    $(".total_attendance_percentagedepartment").each(function () {
        $(this).html(total_attendance_percentage.toFixed(3) + "%");
    });
    $(".total_total_percentagedepartment").each(function () {
        $(this).html(total_percentage.toFixed(3) + "%");
    });

    var task_force_percentage = parseFloat($("#task_force_percentagedepartment").html().split("%")[0]);
    var total_task_force_num = 0.0;
    var total_task_force_point = 0.0;
    $(".task_force_numdepartment").each(function () {
        var task_force_num = parseFloat($(this).html());
        total_task_force_num = total_task_force_num + task_force_num;
    });
    $(".task_force_pointdepartment").each(function () {
        var team_id = $(this).attr('id').split("_")[0];
        var task_force_point = (parseFloat($("#" + team_id + "_task_force_numdepartment").html()) / total_task_force_num) * task_force_percentage;
        $(this).html(task_force_point.toFixed(3) + "%");
        total_task_force_point = total_task_force_point + task_force_point;
    });
    $(".total_task_force_pointdepartment").each(function () {
        $(this).html(total_task_force_point.toFixed(3) + "%");
    });
    $(".total_task_force_numdepartment").each(function () {
        $(this).html(total_task_force_num.toFixed(3));
    });

    var total_all_total = 0.0;
    var money  = parseFloat($("#ipt_zjj").val());
    var all_total_money = 0.0;
    $(".all_totaldepartment").each(function () {
        var team_id = $(this).attr("id").split("_")[0];
        var hr_per = (parseFloat($("#" + team_id + "_hrdepartment").html().split("%")[0])/hr_total)*parseFloat($("#hr_percentagedepartment").html().split("%")[0])
        var all_total = hr_per + parseFloat($("#" + team_id + "_total_percentagedepartment").html().split("%")[0]) + parseFloat($("#" + team_id + "_task_force_pointdepartment").html().split("%")[0]);
        total_all_total  = total_all_total + all_total;
        var total_money = money*all_total/100.0;
        all_total_money = all_total_money + total_money;
        $("#"+team_id+"_all_total_moneydepartment" ).html(total_money.toFixed(3));
        $("#"+team_id+"_all_total_moneydepartment" ).next().html(total_money.toFixed(3));
        $(this).html(all_total.toFixed(3) + '%')

    });
    $(".total_all_totaldepartment").each(function () {
        $(this).html(total_all_total.toFixed(3) + "%")
    });
    $(".all_total_moneydepartment").each(function () {
        $(this).html(all_total_money.toFixed(3))
        $(this).next().html(all_total_money.toFixed(3))
    });


    var total_violation = 0.0;
    var total_below_quality = 0.0;
    var total_finally_money = 0.0;
    $(".finally_moneydepartment").each(function () {
        var team_id = $(this).attr("id").split("_")[0];
        var violation = parseFloat($("#"+team_id+"_violationdepartment").html());
        var below_quality = parseFloat($("#"+team_id+"_below_qualitydepartment").html());
        var money = parseFloat($("#"+team_id+"_all_total_moneydepartment").html());
        var finally_money = money - violation - below_quality;
        total_below_quality = total_below_quality + below_quality;
        total_violation = total_violation + violation;
        total_finally_money = total_finally_money + finally_money;
        $(this).html(finally_money.toFixed(3))
    });
    $(".total_violationdepartment").each(function () {
        $(this).html(total_violation.toFixed(3));
    });
    $(".total_below_qualitydepartment").each(function () {
        $(this).html(total_below_quality.toFixed(3));
    });
    $(".total_finally_moneydepartment").each(function () {
        $(this).html(total_finally_money.toFixed(3));
    });




    var total_duty_work_hc = 0.0;
    var department_num = 0.0;
    $('.duty_work_hcdepartment').each(function () {
        var duty_work_hc = parseFloat($(this).html());
        department_num = department_num + 1;
        total_duty_work_hc = total_duty_work_hc + duty_work_hc;
    });
    $('.total_duty_workdepartment_hc').each(function () {
        $(this).html(total_duty_work_hc.toFixed(3))
    });
    color_check_2("duty_work_hcdepartment", total_duty_work_hc/department_num);


    var total_over_10_5_time_hc = 0.0;
    $('.over_10_5_time_hcdepartment').each(function () {
        var over_10_5_time_hc = parseFloat($(this).html());
        total_over_10_5_time_hc = total_over_10_5_time_hc + over_10_5_time_hc;
    });
    $(".total_over_10_5_timedepartment_hc").each(function () {
       $(this).html(total_over_10_5_time_hc.toFixed(3));
    });
    color_check_2("over_10_5_time_hcdepartment", total_over_10_5_time_hc/department_num);



    var total_night_work_hc = 0.0;
    $('.night_work_hcdepartment').each(function () {
        var night_work_hc = parseFloat($(this).html());
        total_night_work_hc = total_night_work_hc + night_work_hc;
    });
    $(".total_night_workdepartment_hc").each(function () {
       $(this).html(total_night_work_hc.toFixed(3));
    });
    color_check_2("night_work_hcdepartment", total_night_work_hc/department_num);


    var total_travel_abroad_hc = 0.0;
    $('.travel_abroad_hcdepartment').each(function () {
        var travel_abroad_hc = parseFloat($(this).html());
        total_travel_abroad_hc = total_travel_abroad_hc + travel_abroad_hc;
    });
    $(".total_travel_abroaddepartment_hc").each(function () {
       $(this).html(total_travel_abroad_hc.toFixed(3));
    });

    var total_travel_cn_hc = 0.0;
    $('.travel_cn_hcdepartment').each(function () {
        var travel_cn_hc = parseFloat($(this).html());
        total_travel_cn_hc = total_travel_cn_hc + travel_cn_hc;
    });
    $(".total_travel_cndepartment_hc").each(function () {
       $(this).html(total_travel_cn_hc.toFixed(3));
    });

    var total_teamloading = 0.0
    $('.teamloadingdepartment').each(function () {
        var team_id = $(this).attr("id").split("_")[0];
        var duty_work_hc = parseFloat($("#"+ team_id +"_duty_work_hcdepartment").html());
        var over_10_5_time_hc = parseFloat($("#"+ team_id +"_over_10_5_time_hcdepartment").html());
        var night_work_hc= parseFloat($("#"+ team_id +"_night_work_hcdepartment").html());
        var travel_abroad_hc= parseFloat($("#"+ team_id +"_travel_abroad_hcdepartment").html());
        var travel_cn_hc= parseFloat($("#"+ team_id +"_travel_cn_hcdepartment").html());
        var result = ((duty_work_hc/total_duty_work_hc)*duty_work_percentage + (over_10_5_time_hc/total_over_10_5_time_hc)*over_10_5_time_percentage + (night_work_hc/total_night_work_hc)*night_work_percentage + (travel_abroad_hc/total_travel_abroad_hc)*travel_abroad_percentage + (travel_cn_hc/total_travel_cn_hc)*travel_cn_percentage) * 100/(duty_work_percentage+over_10_5_time_percentage+night_work_percentage+travel_abroad_percentage+travel_cn_percentage)
        total_teamloading = total_teamloading + result;
        $(this).html(result.toFixed(3) + "%")
    });

    $(".total_teamloadingdepartment").each(function () {
        $(this).html(total_teamloading.toFixed(3) + "%")
    });

    $('.change_percentage').each(function () {
        var team_id = $(this).attr("id").split("_")[0];
        var this_year = parseFloat($("#"+team_id+"_all_total_moneydepartment").html());
        var last_year = parseFloat($("#"+team_id+"_last_year_money").html());
        $(this).html(((this_year/last_year)*100.0).toFixed(3)+"%")

    });



}

$("#team_data").click(function () {
    $(this).css({"background-color":"#2d2b2b","color":"#ececec","box-shadow":"0px 0px 10px 4px #6b7275"});
    $('#department_data').removeAttr("style");

    $('#table_score_team').css("display","block");
    $('#table_score_department').css("display","none")

    // $('.teamdata').each(function () {
    //     $(this).css("display","block")
    // });
    // $('.departmentdata').each(function () {
    //     $(this).css("display","none")
    // });
});
$("#department_data").click(function () {
    $(this).css({"background-color":"#2d2b2b","color":"#ececec","box-shadow":"0px 0px 10px 4px #6b7275"});
    $('#team_data').removeAttr("style");
    $('#table_score_department').css("display","block");
    $('#table_score_team').css("display","none")



    // $('.departmentdata').each(function () {
    //     $(this).css("display","block")
    // });
    // $('.teamdata').each(function () {
    //     $(this).css("display","none")
    // });
});

function color_check() {
  $(".gs_rate").each(function () {
      var gs_rate = parseFloat($(this).html().split("%")[0]);
      if (gs_rate >= 100.0){
          $(this).css("color","green")
      } else{
          $(this).css("color","black");
          $(this).css("font-weight","");
      }
  });
  $(".patent_rate").each(function () {
      var patent_rate = parseFloat($(this).html().split("%")[0])
      if (patent_rate >= 100.0){
          $(this).css("color","green")
      } else{
          $(this).css("color","black");
          $(this).css("font-weight","");
      }
  });
  $(".gs_ratedepartment").each(function () {
      var gs_ratedepartment = parseFloat($(this).html().split("%")[0])
      if (gs_ratedepartment >= 100.0){
          $(this).css("color","green")
      } else{
          $(this).css("color","black");
          $(this).css("font-weight","");
      }
  });
  $(".patent_ratedepartment").each(function () {
      var patent_ratedepartment = parseFloat($(this).html().split("%")[0])
      if (patent_ratedepartment >= 100.0){
          $(this).css("color","green")
      } else{
          $(this).css("color","black");
          $(this).css("font-weight","");
      }
  });
};


function input_check() {
    if(number_check($("#gs_weightdepartment").html(),"部級金石專案") && number_check($("#patent_weightdepartment").html(),"部級專利提案") && number_check($("#taxdeduction_weightdepartment").html(),"部級稅務抵扣") && number_check($("#gs_weight").html(),"課級金石專案") && number_check($("#patent_weight").html(),"課級專利提案") && number_check($("#taxdeduction_weight").html(),"課級稅務抵扣") && percentage_check($("#proposal_percentage").html(),"課級數據智權提案") && percentage_check($("#exceed_expected_percentage").html(),"課級數據exceed_expected") && percentage_check($("#idl_percentage").html(),"課級數據idl(受到表揚次數)") && percentage_check($("#duty_work_percentage").html(),"課級數據義務時長") && percentage_check($("#over_10_5_time_percentage").html(),"課級數據超時10.5") && percentage_check($("#night_work_percentage").html(),"課級數據夜班天次") && percentage_check($("#travel_abroad_percentage").html(),"課級數據國外出差天次") && percentage_check($("#travel_cn_percentage").html(),"課級數據國內出差天次") && percentage_check($("#leave_percentage").html(),"課級數據離職率") && percentage_check($("#task_force_percentage").html(),"課級數據task force") && percentage_check($("#percentage_1").html(),"課級數據 智權+考勤+客戶評價") && percentage_check($("#proposal_percentagedepartment").html(),"部級數據智權提案") && percentage_check($("#exceed_expected_percentagedepartment").html(),"部級數據exceed_expected") && percentage_check($("#idl_percentagedepartment").html(),"部級數據idl(受到表揚次數)") && percentage_check($("#duty_work_percentagedepartment").html(),"部級數據義務時長") && percentage_check($("#over_10_5_time_percentagedepartment").html(),"部級數據超時10.5") && percentage_check($("#night_work_percentagedepartment").html(),"部級數據夜班天次") && percentage_check($("#travel_abroad_percentagedepartment").html(),"部級數據國外出差天次") && percentage_check($("#travel_cn_percentagedepartment").html(),"部級數據國內出差天次") && percentage_check($("#leave_percentagedepartment").html(),"部級數據離職率") && percentage_check($("#task_force_percentagedepartment").html(),"課級數據task force") && percentage_check($("#percentage_1department").html(),"部級數據 智權+考勤+客戶評價") && percentage_check($("#hr_percentagedepartment").html(),"部級數據 HR")){
        return true
    }else {
        return false
    }
}

function percentage_check(a,title) {
    var b = a.split("%")
    if (b.length == 2){
        if(Number(b[0]) || b[0]=="0"){
             if(title.indexOf('課級') > -1){
                // 科
                $('#department_error_prompt').html("");
            }else {
               $('#team_error_prompt').html("");
            }
            return true
        }else {
            if(title.indexOf('課級') > -1){
                // 科
                $('#department_error_prompt').html(title + "請確認輸入欄位輸入的是否為一個正確的百分數");
            }else {
               $('#team_error_prompt').html(title + "請確認輸入欄位輸入的是否為一個正確的百分數");
            }
            return false
        }
    }else{
        if(title.indexOf('課級') > -1) {
            // 科
            $('#department_error_prompt').html(title + "請確認輸入欄位是否存在且僅存在一個百分號'%'");
        }else {
             $('#team_error_prompt').html(title + "請確認輸入欄位是否存在且僅存在一個百分號'%'");
        }

        return false
    }
}

function number_check(a,title) {
    if(Number(a) || a =="0"){
        if(title.indexOf('課級') > -1){
                // 科
                $('#department_error_prompt').html("");
            }else {
               $('#team_error_prompt').html("");
            }
        return true
    }else {
        if(title.indexOf('課級') > -1) {
            // 科
            $('#department_error_prompt').html(title+"權重欄位數據類型不正確，請輸入一個整數或小數");
        }else {
            $('#team_error_prompt').html(title+"權重欄位數據類型不正確，請輸入一個整數或小數");
        }

        return false
    }
}
//
function money_check() {
    var money_total = parseFloat($("#ipt_zjj").val()) + parseFloat($("#ipt_td").val()) + parseFloat($("#ipt_qt").val());
    $("#ipt_z").val(money_total);
    sum_team();
};

function color_check_2(class_name,avg) {
    $("."+class_name).each(function () {
        var num = parseFloat($(this).html());
        if (num >= avg) {
            $(this).css("color","green");
        }else{
            $(this).css("color","black");
            $(this).css("font-weight","");
        }
    })
}

function percentage_check_2() {
    var flag = false;
    if (parseFloat($("#percentage_1").html().split("%")[0]) + parseFloat($("#task_force_percentage").html().split("%")[0]) != 100.0) {
       $('#department_error_prompt').html("課級百分比之和不為100，可能會導致獎金分配異常");
       flag = true;
    }
    if (parseFloat($("#proposal_percentage").html().split("%")[0]) + parseFloat($("#exceed_expected_percentage").html().split("%")[0]) + parseFloat($("#idl_percentage").html().split("%")[0]) + parseFloat($("#duty_work_percentage").html().split("%")[0]) +parseFloat($("#over_10_5_time_percentage").html().split("%")[0]) + parseFloat($("#night_work_percentage").html().split("%")[0]) + parseFloat($("#travel_abroad_percentage").html().split("%")[0]) + parseFloat($("#travel_cn_percentage").html().split("%")[0]) + parseFloat($("#leave_percentage").html().split("%")[0]) != 100.0){
        $('#department_error_prompt').html("課級百分比之和不為100，可能會導致獎金分配異常");
        flag = true;
    }
    if (parseFloat($("#hr_percentagedepartment").html().split("%")[0]) + parseFloat($("#percentage_1department").html().split("%")[0]) + parseFloat($("#task_force_percentagedepartment").html().split("%")[0]) != 100.0) {
        $('#team_error_prompt').html("部級百分比之和不為100，可能會導致獎金分配異常");
        flag = true;
    }
    if (parseFloat($("#proposal_percentagedepartment").html().split("%")[0]) + parseFloat($("#exceed_expected_percentagedepartment").html().split("%")[0]) + parseFloat($("#idl_percentagedepartment").html().split("%")[0]) + parseFloat($("#duty_work_percentagedepartment").html().split("%")[0]) +parseFloat($("#over_10_5_time_percentagedepartment").html().split("%")[0]) + parseFloat($("#night_work_percentagedepartment").html().split("%")[0]) + parseFloat($("#travel_abroad_percentagedepartment").html().split("%")[0]) + parseFloat($("#travel_cn_percentagedepartment").html().split("%")[0]) + parseFloat($("#leave_percentagedepartment").html().split("%")[0]) != 100.0){
        $('#team_error_prompt').html("部級百分比之和不為100，可能會導致獎金分配異常");
        flag = true;
    }
     if (!flag) {
        $('#team_error_prompt').html("");
    }
}