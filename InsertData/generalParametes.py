# coding:utf-8
"""
@note: the parametes for this project
@author: Sara
"""


class GeneralParameters:
    def __init__(self):
        pass

    # connect oracle 所需的信息
    username = 'eerf_user'
    password = '123456'
    oracle_path = '10.175.94.58:1528/EERFTESTDB'
    # oracle_path = '10.175.94.58:1529/EERFDB'

    # 手动资料路径
    file_root_path = 'D:\OracleData\EERF\Manual'
    log_txt_path = r"D:\OracleData\EERF\InsertLog"

    # EERF 系统所需的 表格名称
    bureau_table = 'ebureau'  # 製造處/機能處/廠處
    department_table = 'edepartment'  # 部級
    subject_table = 'esubject'  # 課級
    group_table = 'egroup'  # 組級
    line_table = 'eline'  # 線級
    deputy_table = "edeputy"  # 副職
    employee_table = "eemployee"  # 副職
    demand_table = 'edemand'  # 招募情況
    recruit_table = 'erecruit'  # 人力需求
    crd_table = 'ecrd'  # 刷卡記錄
    attendanceanomaly_table = 'EATTENDANCEANOMALY'
    attendancehistory_table = 'EATTENDANCEHISTORY'
    falseattendacne_table = 'EFALSEATTENDANCE'
    email_table = 'EEMAIL'
    leave_work_table = 'edimission'  # 離職
    over_hours_table = 'eoverhours'  # 加班時數
    classes_table = "eclasses"  # 班別
    leader_table = "eleader"  # 部長/Group
    team_table = "eteam"  # Function Team
    humans_table = "ehumans"  # 時實人力狀況/天
    total_mans_table = "etotalmans"  # 總人力
    timeout_table = "etimeout"  # 超時
    section_timeout_table = "esectiontimeout"  # 科级超時
    leave_num_table = "eleavenum"  # 離職人數
    leave_prob_table = "eleaveprob"  # 離職率
    greater_than_table = "egreaterthan"  # 大於某點人次
    section_greater_than_table = "esectiongreaterthan"  # 科级大於某點人次
    night_shift_table = "enightshift"  # 晚班人數
    section_night_shift_table = "esectionnightshift"  # 科级晚班人數
    duty_work_table = "edutywork"  # 超時加班(義務)
    section_work_table = "esectiondutywork"  # 科级超時加班(義務)
    rest_table = "erest"  # 調休時數
    subject_team_table = "esubjectteam"  # 課與Function Team
    attendance_table = "eattendance"  # 員工考勤

    # 盛佳 报表需求
    late_meal_fee_table = "elatemealfee"    # 误餐费
    lmf_crd_table = 'elmfcrd'   # 刷卡記錄
    lmf_attendance_table = "elmfattendance"  # 員工考勤
    personal_work_time_table = "epersonalworktime"  # 員工考勤月工作时长
    lmf_personal_work_time_table = "elmfpersonalworktime"  # 員工考勤实时工作时长

    # 金石专案结案申请单
    golden_stone_project_table = 'egoldenstoneproject'
    register_project_table = 'eregisterproject'
    # golden stone project by leader
    gspbyleader_table = 'egspbyleader'
    # 国内外出差信息表
    etravel_table = 'etravel'
    # 出差次数表 每个leader 每个team 每个月 国内/国外 出差次数
    etravelcount_table = 'etravelcount'

    # 盛佳 报表需求
    late_meal_fee_order_string = '''l_datetime,l_employee,l_cname,l_leader,l_interval,l_weeknum,l_tenlate,l_eightlate,l_ninelate,l_elevenlate'''
    lmf_crd_order_string = '''c_legal,c_plant,eemployee_id,c_datetime,c_datetype,
        c_code,c_type,c_workcrad,c_firstcrad,c_closedcard,c_lastcard'''
    lmf_pzms_order_string = '''eemployee_id,c_datetime,c_datetype,c_code,c_type,
        c_plant,c_workcrad,c_firstcrad,c_closedcard,c_lastcard'''
    lmf_attendance_order_string = '''a_datetime,a_employee,a_name,a_leader,a_team,a_interval,a_totalhours,a_avghours,a_maxhours,a_totaldays,
        a_totaloverhours,a_avgoverhours,a_maxoverhours,a_totaldutyhours,a_avgdutyhours,a_maxdutyhours,a_dutydays,
        a_avglastcard,a_maxlastcard,a_nightnum,a_offduty,a_unoffduty,a_eightlate,a_eighttotal,a_tenlate'''

    # 资料的路径
    attendanceanomaly_xls = [[r'D:\OracleData\EERF\Attendanceanomaly', u'Attendance.csv'], [r'D:\OracleData\EERF\Attendanceanomaly', u'Attendance(1).csv']]
    pzmsattendanceanomaly_xls = [[r'D:\OracleData\EERF\PZMSAttendanceanomaly', u'PZMSAttendance.xls'], [r'D:\OracleData\EERF\Attendanceanomaly', u'PZMSAttendance(1).xls']]
    falseattendance_xls = [[r'D:\OracleData\EERF\Attendanceanomaly', u'False_Report.csv'], [r'D:\OracleData\EERF\Attendanceanomaly', u'False_Report(1).csv']]
    email_xls = [r'D:\OracleData\EERF\EMAIL', u'EmpBaseInfo']
    employee_xls = [r'D:\OracleData\EERF\EAMP', u'EmpRelChangeInfo']
    demand_xls = [r'D:\OracleData\EERF\FHR', u'人力需求']
    recruit_xls = [r'D:\OracleData\EERF\FHR', u'錄用進度表']
    crd_xls = [r'D:\OracleData\EERF\Attence', u'ExportData']
    pams_xls = [r'D:\OracleData\EERF\PZMS', u'Unusual']
    # crd_xls = [r'D:\OracleData\EERF\Attendence', u'ExportData']
    leave_work_xls = [r'D:\OracleData\EERF\EISP', u'Dimission']
    # 金石结案申请单
    report_xls = [r'D:\OracleData\EERF\EISP_2', u'']
    over_hours_xls = [r'D:\OracleData\EERF\Overtime\download', u'AttendanceTotal']
    crd_need_title = [u"法人", u"工作廠區", u"工號", u"日期", u"日期類型", u"班別代碼",
                      u"班別類型", u"上班時間", u"刷卡時間", u"下班時間", u"刷卡時間"]

    lmf_crd_xls = [r'D:\OracleData\EERF\Attendance(Daily)', u'ExportData']
    week_crd_xls = [r'D:\OracleData\EERF\Attendance(Week)', u'ExportData']
    lmf_pzms_xls = [r'D:\OracleData\EERF\PZMS(Daily)', u'ExportData']
    week_pzms_xls = [r'D:\OracleData\EERF\PZMS(Week)', u'ExportData']

    # Oracle EERF 系统中，各个表格的栏位
    bureau_order_string = 'b_bureau, b_leadernum, b_leader, b_up'
    department_order_string = 'd_department, d_leadernum, d_leader, ebureau_id'
    subject_order_string = 's_subject, s_leadernum, s_leader, edepartment_id'
    employee_auto_order_string = '''e_id, e_pwd, e_cname, e_grade, e_direct, e_difference, e_management, 
                        e_managers, e_place, ebureau_id, edepartment_id, esubject_id, egroup_id, 
                        eline_id, e_DRI, e_authority, e_status, e_lastdate,e_category,e_leader,e_functionteam'''


    employee_manual_order_string = '''e_id, e_pwd, e_cname, e_grade, e_difference, e_management, e_managers, 
                                    ebureau_id, edepartment_id, esubject_id, e_leader, e_functionteam, 
                                    e_place, e_category, e_expiringdate, e_status'''

    deputy_order_string = 'eemployee_id, d_character, d_bureau, d_department, d_subject, d_group, d_line'

    demand_order_string = '''d_urgency,d_number,d_status,d_frequency,d_bureau,d_department,d_abbreviation,d_position,
        d_amount,d_finished,d_offer,d_unfinish,d_requirement,d_experience,d_recruiter,d_grade,d_cellphone,d_degree,
        d_working,d_demand01,d_demand02,d_request,d_require,d_application,d_register'''

    recruit_order_string = '''r_status,r_number,r_name,r_sex,r_Idcard,r_contact,r_interview,r_bureau,r_department,
        r_position,r_demand01,r_demand02,r_source,r_recruiter,r_degree,r_grade,r_result01,r_result02,r_progress,
        r_healthcheck,r_checkresult,r_register,r_anomaly'''

    crd_order_string = '''c_legal,c_plant,eemployee_id,c_datetime,c_datetype,
        c_code,c_type,c_workcrad,c_firstcrad,c_closedcard,c_lastcard'''

    pzms_order_string = '''eemployee_id,c_datetime,c_datetype,c_code,c_type,
        c_plant,c_workcrad,c_firstcrad,c_closedcard,c_lastcard'''

    leave_work_order_string = '''d_step,d_number,d_cname,d_department,d_grade,d_management,
                    d_reason01,d_reason02,d_reason03,d_firstdate,d_seniority,d_lastdate,d_requestdate'''

    total_mans_order_string = 't_datetime,t_headcount,t_reserve,t_leave,t_engineers,t_technician,t_supporter,t_loan'

    greater_than_order_string = '''g_datetime, g_leader, g_ontime, g_overtime, g_9_hours
        , g_9_5_hours, g_10_hours, g_10_5_hours, g_11_hours, g_11_5_hours, g_12_hours, g_12_5_hours'''
    section_greater_than_order_string = '''g_datetime, g_section, g_ontime, g_overtime, g_9_hours
        , g_9_5_hours, g_10_hours, g_10_5_hours, g_11_hours, g_11_5_hours, g_12_hours, g_12_5_hours'''

    personal_work_time_string = '''p_datetime, p_employee, p_leader, p_9_hours, p_9_5_hours, 
            p_10_hours, p_10_5_hours, p_11_hours, p_11_5_hours, p_12_hours, p_12_5_hours'''
    
    lmf_personal_work_time_string = '''p_datetime, p_employee, p_leader, p_9_hours, p_9_5_hours, 
        p_10_hours, p_10_5_hours, p_11_hours, p_11_5_hours, p_12_hours, p_12_5_hours'''
    
    night_shift_order_string = 'n_datetime,n_leader,n_number'
    section_night_shift_order_string = 'n_datetime,n_section,n_number'

    duty_work_order_string = 'd_datetime,d_leader,d_number,d_population'
    section_work_order_string = 'd_datetime,d_section,d_number,d_population,d_leader'

    rest_order_string = '''r_datetime,r_employee,r_effectivity01,r_overtime01,r_rest01,
                        r_effectivity02,r_overtime02,r_rest02,r_effectivity03,r_nightshift,r_totalrest'''

    over_hours_order_string_28 = '''h_place, h_department, eemployee_id, h_grade, h_type, h_yearmouth
        , h_01, h_02, h_03, h_04, h_05, h_06, h_07, h_08, h_09, h_10
        , h_11, h_12, h_13, h_14, h_15, h_16, h_17, h_18, h_19, h_20
        , h_21, h_22, h_23, h_24, h_25, h_26, h_27, h_28
        , h_32, h_33, h_34'''

    over_hours_order_string_29 = '''h_place, h_department, eemployee_id, h_grade, h_type, h_yearmouth
        , h_01, h_02, h_03, h_04, h_05, h_06, h_07, h_08, h_09, h_10
        , h_11, h_12, h_13, h_14, h_15, h_16, h_17, h_18, h_19, h_20
        , h_21, h_22, h_23, h_24, h_25, h_26, h_27, h_28, h_29
        , h_32, h_33, h_34'''

    over_hours_order_string_30 = '''h_place, h_department, eemployee_id, h_grade, h_type, h_yearmouth
        , h_01, h_02, h_03, h_04, h_05, h_06, h_07, h_08, h_09, h_10
        , h_11, h_12, h_13, h_14, h_15, h_16, h_17, h_18, h_19, h_20
        , h_21, h_22, h_23, h_24, h_25, h_26, h_27, h_28, h_29, h_30
        , h_32, h_33, h_34'''

    over_hours_order_string_31 = '''h_place, h_department, eemployee_id, h_grade, h_type, h_yearmouth
        , h_01, h_02, h_03, h_04, h_05, h_06, h_07, h_08, h_09, h_10
        , h_11, h_12, h_13, h_14, h_15, h_16, h_17, h_18, h_19, h_20
        , h_21, h_22, h_23, h_24, h_25, h_26, h_27, h_28, h_29, h_30
        , h_31, h_32, h_33, h_34'''

    classes_order_string = '''c_code, c_type, c_hours, c_firstup, c_firstdown, c_secondeup, c_secondedown, c_beginover,
        c_description, c_category'''
    leader_order_string = 'edepartment_id, l_leadernum, l_leader, l_group, edepartment_num'
    team_order_string = 't_place, t_team, eleader_id'
    humans_order_string = 'h_cname, h_num, h_ename, h_group, h_team, h_taiwan, h_mesome, h_technician, h_spindrift'
    timeout_order_string = 't_datetime, t_leader, t_over9, t_over95, t_over10, t_over105, t_over11'
    section_timeout_order_string = 't_datetime, t_section, t_over9, t_over95, t_over10, t_over105, t_over11'
    leave_num_order_string = 'l_datetime ,l_leader ,l_leavenum'
    leave_prob_order_string = 'l_datetime, l_leaveprob'
    subject_team_order_string = 'st_subject, st_place, st_team'
    attendance_order_string = '''a_datetime,a_employee,a_name,a_leader,a_team,a_totalhours,a_avghours,a_maxhours,a_totaldays,
        a_totaloverhours,a_avgoverhours,a_maxoverhours,a_totaldutyhours,a_avgdutyhours,a_maxdutyhours,a_dutydays,
        a_avglastcard,a_maxlastcard,a_nightnum,a_offduty,a_unoffduty,A_EIGHTTOTAL'''
    eattendanceanomaly_order_string = '''A_LEGAL,A_LOCATION,A_BUREAU,A_DEPARTMENT,A_CLASS,A_EMPLOYEEID,A_NAME,A_DATETIME,A_DATETYPE,A_CLASSCODE,A_TYPE,A_WORKCRAD,A_FIRSTCRAD,A_ANOMALYTYPE,A_LATETIME,A_REPLYTYPE,A_CLOSEDCARD,A_LASTCARD,A_ANOMALYTYPE2,A_EARLYTIME,A_REPLYTYPE2'''
    efalseattendance_order_string = '''F_LEGAL,F_LOCATION,F_BUREAU,F_DEPARTMENT,F_CLASS,F_EMPLOYEEID,F_NAME,F_GRADE,F_DATETIME,F_FALSETYPE,F_FALSEHOURS'''
    eemail_order_string = '''E_NAME,E_EMPLOYEE,E_EMAIL'''
    max_data_len = 50000

    golden_stone_order_string = '''e_project_id, e_department, e_factory, e_project_category, e_project_name, e_form_status,
    e_signing_steps, e_performance, e_sponsor_name, e_sponsor_id, e_complete_date, e_create_date, e_subject_name,
    e_pre_signing_steps, e_sign_opinion, e_leader '''

    register_project_order_string = '''e_project_id, e_department, e_factory, e_project_category, e_project_name, e_form_status,
    e_signing_steps, e_performance, e_sponsor_name, e_sponsor_id, e_complete_date, e_create_date, e_subject_name,
    e_pre_signing_steps, e_sign_opinion, e_leader '''

    gspbyleader_order_string = 'e_functionteam,e_leader,e_register_num, e_closed_num, e_no_closed_num, e_performance, e_team_target, e_team_hc,e_year,e_per_benefit'

    etravel_order_string = '''ee_id, ee_name, e_travel_type, e_travel_id, e_status, e_start_date, e_end_date, 
        e_travel_days, e_functionteam, e_leader'''

    etravelcount_order_string = '''t_leader, t_functionteam, t_type, t_count, t_datetime'''

    # matrix need parameters
    config_file_path = 'config/config.ini'
    already_open_file_mark = "~$"
    matrix_config_keyword = 'Configs'
    matrix_items_keyword = 'Item'
    matrix_keyword = "matrix"
    
    # EmpNo_Excel
    EmpNo_Excel_path = r"D:\OracleData\EERF\EmpNo_Excel\EmpNo.xls"
