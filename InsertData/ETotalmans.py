# coding:utf-8
"""
@note: 计算考勤资料与离职人数
@note: get the data to insert
@author: F
"""
import collections
import os
import time
import logging
import calendar
import decimal

from datetime import datetime, timedelta
from DMLData import oracle
from TableData import ExportTableData
from generalParametes import GeneralParameters

# 针对 Oracle 与 Python 编码不一致
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.AL32UTF8'


class ArrangeDB:
    def __init__(self):
        self.LeaderNameForId_dic = {}
        self.SectionNameForId_dic = {}
        self.setLog()
        logging.info("Beginning ArrangeDB!!")
        self.dml_obj = oracle()
        self.createFolder()
        try:
            print "----- Beginning ArrangeDB!!"
            # self.insertDBData()    # 月1號生成  總人力
            self.insertLeaveNum()   # 月1號生成 離職人數
            # self.insertLeaveProb()   # 月1號生成 離職率

            # self.insertOverHours()    # 月5號生成  加班時數
            # self.insertAttendance()  # 月5號生成   員工个人考勤信息
            # self.insertTimeout()    # 月5號生成 工作超時
            # self.insertGreaterThanData() # 月5號生成 大於某點人次
            # self.insertNightData() # 月5號生成 晚班人數
            # self.insertDutyWork() # 月5號生成 超時加班(義務)
            # self.insertRest() # 調休時數

            # self.insertSectionDutyWork() # 新增 月5號生成 超時加班(義務) 科级
            # self.insertSectionNightData()  # 新增 月5號生成 晚班人數 科级
            # self.insertSectionTimeout()  # 新增 月5號生成 工作超時 科级
            # self.insertSectionGreaterThanData()  # 新增 月5號生成 大於某點人次 科级

            # self.insertLmfPersonalWorkTime() # 每日执行,计数工作时长
            # self.insertLateMealFee()  # 误餐费
            # self.insertLMFAttendance()
        except Exception as e:
            print(e)
            logging.info(str(e))
        print "----- Finished ArrangeDB!!"
        logging.info("Finished ArrangeDB!!")

    def printData(self, data):
        '''
        print the data
        '''
        for row, row_data in enumerate(data):
            print "row:", row, "--",
            for col, each_data in enumerate(row_data):
                #                 print col,each_data,type(each_data)," ",
                #                 print col,each_data," ",
                print col, each_data, type(each_data), " ",
            print ""

    def insertDBData(self):
        """
        @note: 總人力，每一个月的月初，更新 總人力 数据
        @note: 例如: 五月初，计算 到四月底时的总人力
        """
        self.file_object.write("\n ---------------------total_mans_table 总人力----------------------- \n")
        self.writeTxt("insert total_mans_table总人力", "Beginning")
        # 获取日期
        # 1.prior_now_date 上个月一号的日期
        # 2.now_date 这个月一号的日期
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()
        prior_now_date = self.getNewDate(prior_year, prior_mouth, "01")
        now_date = self.getNewDate(this_year, this_mouth, "01")

        if self.dml_obj.selectData("t_id", GeneralParameters.total_mans_table,
                                   "t_datetime = to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss')"):
            print " 已存在 该日期资料"
            print "----- Finished insert total_mans_table!!"
            logging.info("End insertDBData: total_mans_table is already exist!!")
            self.writeTxt("insert total_mans_table总人力", "资料已存在，不需写入数据库")
            return ""

        # 該天總人數  = 浪花 + 常设
        headcount_man_list = self.getList('e_id', GeneralParameters.employee_table, "e_status", u"在職")

        # 在职人数
        reserve_man_list = self.getList('e_id', GeneralParameters.employee_table, "e_status", u"在職")

        # 离职人数
        this_keyword_name = "e_lastdate >= to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss') and " + \
                            "e_lastdate < to_date('" + str(now_date) + "','yyyy-mm-dd hh24:mi:ss')" + \
                            " and e_category ='" + u"常設" + "' and e_status"
        leave_man_list = self.getList('e_id', GeneralParameters.employee_table, this_keyword_name, u"離職")

        # 常設在職師級
        engineers_man_list = self.getList('e_id', GeneralParameters.employee_table,
                                          "e_grade like '%" + u"師" + "%' and e_status = '" + u'在職' + "' and e_category",
                                          u"常設")

        # 常設在職員級
        technician_man_list = self.getList('e_id', GeneralParameters.employee_table,
                                           "e_grade like '%" + u"員" + "%' and e_status ='" + u'在職' + "' and e_category",
                                           u"常設")

        # 浪花 = 借調 + 支援
        supporter_man_list = self.getList('e_id', GeneralParameters.employee_table,
                                          "e_status = '" + u'在職' + "' and e_category", u"支援")

        # 借調人數
        loan_man_list = self.getList('e_id', GeneralParameters.employee_table,
                                     "e_status = '" + u'在職' + "' and e_category", u"借調")

        # insertData 写进 db 时， 需要的 数组格式 [[],[],[],....]
        data = [[prior_now_date, len(headcount_man_list), len(reserve_man_list), len(leave_man_list),
                 len(engineers_man_list), len(technician_man_list), len(supporter_man_list), len(loan_man_list)]]
        self.insertExcept(data, GeneralParameters.total_mans_order_string, GeneralParameters.total_mans_table,
                          "insert total_mans_table总人力")
        print "----- Finished insert total_mans_table!!"
        logging.info("End insertDBData!!!")

    def insertLeaveNum(self):
        """
        @note: 離職人數    计算 上一个月的情况
        """
        self.file_object.write("\n ---------------------LeaveNum 离职人数----------------------- \n")
        self.writeTxt("insert LeaveNum离职人数", "Beginning")
        # 获取日期
        # 1.prior_now_date 上个月一号的日期
        # 2.now_date 这个月一号的日期
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()
        prior_now_date = self.getNewDate(prior_year, prior_mouth, "01")
        now_date = self.getNewDate(this_year, this_mouth, "01")

        # 判断 数据库中 是否存在该月数据 避免重复插入
        if self.dml_obj.selectData("l_leader", GeneralParameters.leave_num_table,
                                   "l_datetime=to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss')"):
            print " 已存在 该日期资料"
            print "---Finished insert_leave_num_table!!"
            logging.info("End insertLeaveNum: insert_leave_num_table is already exist!!")
            self.writeTxt("insert LeaveNum离职人数", "资料已存在，不需写入数据库")
            return

        # 通过SQL语句，在 employee_table 中获取 [上个月一号 到 这个月一号] 的离职常设师级员工
        leave_where_sql = "e_lastdate >= to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss')" + \
                          " and e_lastdate < to_date('" + str(now_date) + "','yyyy-mm-dd hh24:mi:ss')" + \
                          " and e_grade like '%" + u"師" + "%' and e_category='" + u"常設" + "'"
        leave_num_tup = self.dml_obj.selectData("e_id,e_leader", GeneralParameters.employee_table, leave_where_sql)

        # 计算每个主管下的离职人数
        leave_num_leader_dic = {}
        for each_tup in leave_num_tup:
            this_leader = each_tup[1]
            if this_leader not in leave_num_leader_dic.keys():
                leave_num_leader_dic[this_leader] = 1
            else:
                leave_num_leader_dic[this_leader] = leave_num_leader_dic[this_leader] + 1

        # 写进 db 时， 需要的 数组格式 [[],[],[],....]
        insert_leave_num_list = []
        for key, value in leave_num_leader_dic.items():
            this_list = [prior_now_date, key, value]
            insert_leave_num_list.append(this_list)

        if insert_leave_num_list:
            self.insertExcept(insert_leave_num_list, GeneralParameters.leave_num_order_string,
                              GeneralParameters.leave_num_table, "insert LeaveNum离职人数")
        else:
            self.writeTxt("insert LeaveNum", "没有计算出数据")
        self.writeTxt("insert LeaveNum离职人数", "Finished")
        print "--- Finished insert_leave_num!!"
        logging.info("End insertLeaveNum!!")

    def insertLeaveProb(self):
        """
        @note:  插入 leave_prob_table 離職率
        @note: 例：在 2018-07-01 当天，计算 2018-06的离职率，就要获取2018-06-01~~2018-07-01
        @note: 的两个时间点的离职人数，由于储存数据的日期有些特殊，故在数据库中检索的范围是：
        @note: 2018-05-01 2018-06-01
        """
        self.file_object.write("\n ---------------------LeaveProb 离职率----------------------- \n")
        self.writeTxt("insert LeaveProb离职率", "Beginning")
        # 获取日期
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()
        # 2019 1 2018 12
        if prior_mouth == 1:
            prior_now_date = self.getNewDate(prior_year - 1, 12, "01")
        else:
            prior_now_date = self.getNewDate(prior_year, prior_mouth - 1, "01")
        now_date = self.getNewDate(prior_year, prior_mouth, "01")
        prior_mouth_date = self.getNewDate(prior_year, prior_mouth, "01")
        this_mouth_date = self.getNewDate(this_year, this_mouth, "01")

        if self.dml_obj.selectData("l_id", GeneralParameters.leave_prob_table,
                                   "l_datetime = to_date('" + str(now_date) + "','yyyy-mm-dd hh24:mi:ss')"):
            print " eLeaveProb 中 已存在该日期 资料"
            print "---Finished insert_leave_prob_table!!"
            logging.info("End insertLeaveProb: insert_leave_prob_table is already exist!!")
            self.writeTxt("insert LeaveProb离职率", "资料已存在，不需写入数据库")
            return

        # 通过SQL语句，在 employee_table 中获取 [上个月一号 到 这个月一号] 的离职常设师级员工
        leave_where_sql = "e_lastdate >= to_date('" + str(prior_mouth_date) + "','yyyy-mm-dd hh24:mi:ss')" + \
                          " and e_lastdate < to_date('" + str(this_mouth_date) + "','yyyy-mm-dd hh24:mi:ss') and " + \
                          "e_grade like '%" + u"師" + "%' and e_category='" + u"常設" + "'"
        total_leave_prob = self.getListLen("e_id", GeneralParameters.employee_table, leave_where_sql)
        total_leave_prob = float(total_leave_prob)
        print 'total_leave_prob:', total_leave_prob, type(total_leave_prob)

        # 师级 月初 总人数
        before_where_sql = "t_datetime = to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss')"
        total_before_number_tup = self.dml_obj.selectData("t_engineers", GeneralParameters.total_mans_table,
                                                          before_where_sql)
        total_before_number_list = [code_tup[0] for code_tup in total_before_number_tup]
        total_before_number_01 = float(total_before_number_list[0])
        print 'total_before_number_01:', total_before_number_01, type(total_before_number_01)

        # 师级 月末 总人数
        now_where_sql = "t_datetime = to_date('" + str(now_date) + "','yyyy-mm-dd hh24:mi:ss')"
        total_now_number_tup = self.dml_obj.selectData("t_engineers", GeneralParameters.total_mans_table, now_where_sql)
        print "total_now_number_tup:", total_now_number_tup
        total_now_number_list = [code_tup[0] for code_tup in total_now_number_tup]
        total_before_number_02 = float(total_now_number_list[0])
        print 'total_before_number_02:', total_before_number_02, type(total_before_number_02)

        this_entry_num = total_before_number_02 - total_before_number_01 + total_leave_prob
        this_leave_prob = (total_leave_prob / (total_before_number_01 + this_entry_num)) * 100

        # 写进 db 时， 需要的 数组格式 [[],[],[],....]
        insert_leave_prob_data = [[now_date, this_leave_prob]]

        if insert_leave_prob_data:
            self.insertExcept(insert_leave_prob_data, GeneralParameters.leave_prob_order_string,
                              GeneralParameters.leave_prob_table, "insert LeaveProb离职率")
        else:
            self.writeTxt("insert LeaveProb离职率", "没有计算出数据")
        self.writeTxt("insert LeaveProb离职率", "Finished")
        print "--- Finished insert_leave_prob!!"
        logging.info("End insertLeaveProb!!")

    def insertOverHours(self):
        """
        @note: 员工提报加班时数汇总数据，写入数据库
        """
        # 获取 员工有效加班 数据
        self.file_object.write("\n ---------------------OverHours 有效加班时数----------------------- \n")
        self.writeTxt("insert OverHours有效加班时数", "Beginning")
        over_hours_path = self.getXlsPath(GeneralParameters.over_hours_xls)
        if not over_hours_path:
            logging.info("End insertOverHours: not over_hours_path")
            self.writeTxt("insert OverHours有效加班时数", "没有 Excel文件")
            self.writeTxt("insert OverHours有效加班时数", "Finished")
            return

        over_hours_list_data = self.getXlsData(over_hours_path)
        for row_data in over_hours_list_data:
            row_data.pop(4)
            row_data.pop(3)

        # 整理这份数据的时间
        this_xls_time = over_hours_list_data[1][9:]
        this_xls_date = self.getXlsDate(this_xls_time)
        insert_over_hours_data = []
        # 如数据库中有 this_xls_date 则不需要插入
        unique_list = self.dml_obj.selectData("h_yearmouth", GeneralParameters.over_hours_table)
        db_code_list = [code_tupe[0] for code_tupe in unique_list]
        if this_xls_date in db_code_list:
            print "-----this OverHours is already exist -------------"
            logging.info("End insertOverHours: this OverHours is already exist!!")
            self.writeTxt("insert OverHours有效加班时数", "资料已存在，不需写入数据库")
            return

        # 整理数据：只要加班那一行，调整数据类型
        # 写进 db 时， 需要的 数组格式 [[],[],[],....]
        for row, each_row in enumerate(over_hours_list_data):
            if each_row[8] == u'調休':
                continue
            elif each_row[8] == u'加班':
                this_row_list = each_row
                this_row_list[8] = this_xls_date
                this_row_list.pop(0)
                this_row_list.pop(0)
                this_row_list.pop(3)
                if type(this_row_list[2]) == float:
                    this_row_list[2] = str(int(this_row_list[2]))
                man_val = this_row_list[2]
                man_pk = self.getFK("e_id", "e_id", man_val, GeneralParameters.employee_table)
                this_row_list[2] = man_pk
                insert_over_hours_data.append(this_row_list)

        if insert_over_hours_data:
            this_xls_time_len = len(this_xls_time) - 3
            if this_xls_time_len == 31:
                self.insertExcept(insert_over_hours_data, GeneralParameters.over_hours_order_string_31,
                                  GeneralParameters.over_hours_table, "insert OverHours有效加班时数")
            elif this_xls_time_len == 30:
                self.insertExcept(insert_over_hours_data, GeneralParameters.over_hours_order_string_30,
                                  GeneralParameters.over_hours_table, "insert OverHours有效加班时数")
            elif this_xls_time_len == 29:
                self.insertExcept(insert_over_hours_data, GeneralParameters.over_hours_order_string_29,
                                  GeneralParameters.over_hours_table, "insert OverHours有效加班时数")
            else:
                self.insertExcept(insert_over_hours_data, GeneralParameters.over_hours_order_string_28,
                                  GeneralParameters.over_hours_table, "insert OverHours有效加班时数")
            logging.info("End insertOverHours!!")
        else:
            self.writeTxt("insert OverHours有效加班时数", "Excel文件中没有数据")
        self.writeTxt("insert OverHours有效加班时数", "Finished")
        logging.info("End insertOverHours: insert_over_hours_data is null")

    def insertTimeout(self):
        """
        @note: 要从数据库中获取 前一个月的 刷卡 数据
        """
        self.file_object.write("\n ---------------------Timeout 工作超时----------------------- \n")
        self.writeTxt("insert Timeout工作超时", "Beginning")
        # 获得 今年今月
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()

        # 判断 数据库中 是否存在该月数据 避免重复插入
        this_mouth_date = self.getNewDate(prior_year, prior_mouth, "05")
        timeout_where_string = "t_datetime=to_date('" + str(this_mouth_date) + "','yyyy-mm-dd hh24:mi:ss')"
        # etimeout表中部级领导英文名
        db_datetime_tup = self.dml_obj.selectData("t_leader", GeneralParameters.timeout_table, timeout_where_string)
        db_datetime_list = [code_tup[0] for code_tup in db_datetime_tup]
        if db_datetime_list:
            print " 已存在 该日期资料"
            print "---Finished insert timeout_table!!"
            logging.info("End insertTimeout: timeout_table is already exist!!")
            self.writeTxt("insert Timeout工作超时", "资料已存在，不需写入数据库")
            return

        # 上个月1号
        prior_now_date = self.getNewDate(prior_year, prior_mouth, "01")
        # 这个月1号
        now_date = self.getNewDate(this_year, this_mouth, "01")

        # 通过SQL语句，在 刷卡信息中提取 [上个月一号 到 这个月一号] 的常设师级员工的刷卡记录
        crd_where_sql = "c_firstcrad is not null" + \
                        " and c_lastcard is not null " + \
                        " and c_datetype !='" + u"節假日" + "'" + \
                        " and c_datetime >= to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss')" + \
                        " and c_datetime < to_date('" + str(now_date) + "','yyyy-mm-dd hh24:mi:ss') order by c_datetime"
        all_data_dic = self.getTimeoutData(crd_where_sql)

        # 获取 超时的人次数据
        timeout_data_dic = self.arrangeTimeoutData(all_data_dic)

        # 所有的 主管都要写入 DB
        # 所有主管列表元组
        all_leader_tup = self.dml_obj.selectData("e_ename", GeneralParameters.employee_table, "e_ename is not null")
        # 所有主管列表
        all_leader_list = [code_tup[0] for code_tup in all_leader_tup]
        for each_leader in all_leader_list:
            if each_leader not in timeout_data_dic.keys():
                timeout_data_dic[each_leader] = [each_leader, 0, 0, 0, 0, 0]

        # 写进 db 时， 需要的 数组格式 [[],[],[],....]
        insert_time_out_list = []
        for key, value in timeout_data_dic.items():
            this_key_list = value
            # 超9h 也要包含在 超8h 数据中，以此类推
            this_key_list[1] = value[1] + value[2] + value[3] + value[4] + value[5]
            this_key_list[2] = value[2] + value[3] + value[4] + value[5]
            this_key_list[3] = value[3] + value[4] + value[5]
            this_key_list[4] = value[4] + value[5]
            this_key_list.insert(0, this_mouth_date)
            insert_time_out_list.append(value)
            print "value:", value

        if insert_time_out_list:
            self.insertExcept(insert_time_out_list, GeneralParameters.timeout_order_string,
                              GeneralParameters.timeout_table, "insert Timeout工作超时")
        else:
            self.writeTxt("insert Timeout工作超时", "没有计算出数据")
        self.writeTxt("insert Timeout工作超时", "Finished")
        print "---Finished insertTimeout!!"
        logging.info("End insertTimeout!!")

    def insertSectionTimeout(self):
        """
        @note: 要从数据库中获取 前一个月的 刷卡 数据 -- 科级
        """
        self.file_object.write("\n ---------------------Section Timeout 工作超时----------------------- \n")
        self.writeTxt("insert Section Timeout工作超时", "Beginning")
        # 获得 今年今月
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()

        # 判断 数据库中 是否存在该月数据 避免重复插入
        this_mouth_date = self.getNewDate(prior_year, prior_mouth, "05")

        timeout_where_string = "t_datetime=to_date('" + str(this_mouth_date) + "','yyyy-mm-dd hh24:mi:ss')"
        db_datetime_tup = self.dml_obj.selectData("t_section", GeneralParameters.section_timeout_table,
                                                  timeout_where_string)
        db_datetime_list = [code_tup[0] for code_tup in db_datetime_tup]
        if db_datetime_list:
            print " 已存在 该日期资料"
            print "---Finished insert section_timeout_table!!"
            logging.info("End insertSectionTimeout: section_timeout_table is already exist!!")
            self.writeTxt("insert SectionTimeout工作超时", "资料已存在，不需写入数据库")
            return

        prior_now_date = self.getNewDate(prior_year, prior_mouth, "01")
        now_date = self.getNewDate(this_year, this_mouth, "01")

        # 通过SQL语句，在 刷卡信息中提取 [上个月一号 到 这个月一号] 的常设师级员工的刷卡记录
        crd_where_sql = "c_firstcrad is not null" + \
                        " and c_lastcard is not null " + \
                        " and c_datetype !='" + u"節假日" + "'" + \
                        " and c_datetime >= to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss')" + \
                        " and c_datetime < to_date('" + str(now_date) + "','yyyy-mm-dd hh24:mi:ss') order by c_datetime"
        all_data_dic = self.getTimeoutData(crd_where_sql)

        # 获取 超时的人次数据
        timeout_data_dic = self.arrangeSectionTimeoutData(all_data_dic)

        # 所有的 科级名都要写入 DB
        all_section_tup = self.dml_obj.selectData("e_functionteam", GeneralParameters.employee_table,
                                                  "e_functionteam is not null and e_functionteam != 'Magma'")
        all_section_list = [code_tup[0] for code_tup in all_section_tup]
        all_section_list = list(set(all_section_list))
        for each_section in all_section_list:
            if each_section not in timeout_data_dic.keys():
                timeout_data_dic[each_section] = [each_section, 0, 0, 0, 0, 0]

        # 写进 db 时， 需要的 数组格式 [[],[],[],....]
        insert_time_out_list = []
        for key, value in timeout_data_dic.items():
            this_key_list = value
            # 超9h 也要包含在 超8h 数据中，以此类推
            this_key_list[1] = value[1] + value[2] + value[3] + value[4] + value[5]
            this_key_list[2] = value[2] + value[3] + value[4] + value[5]
            this_key_list[3] = value[3] + value[4] + value[5]
            this_key_list[4] = value[4] + value[5]
            this_key_list.insert(0, this_mouth_date)
            insert_time_out_list.append(value)
            print "value:", value

        if insert_time_out_list:
            self.insertExcept(insert_time_out_list, GeneralParameters.section_timeout_order_string,
                              GeneralParameters.section_timeout_table, "insert SectionTimeout工作超时")
        else:
            self.writeTxt("insert SectionTimeout工作超时", "没有计算出数据")
        self.writeTxt("insert SectionTimeout工作超时", "Finished")
        print "---Finished insertSectionTimeout!!"
        logging.info("End insertSectionTimeout!!")

    def insertRest(self):
        """
        @note: 计算调休
        """
        self.file_object.write("\n ---------------------Rest 调休----------------------- \n")
        self.writeTxt("insert Rest调休", "Beginning")
        # 获取日期
        # 1.prior_now_date 上个月一号的日期
        # 2.now_date 这个月一号的日期
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()
        prior_now_date = self.getNewDate(prior_year, prior_mouth, "01")
        now_date = self.getNewDate(this_year, this_mouth, "01")

        this_mouth_date = self.getNewDate(prior_year, prior_mouth, "05")
        if self.dml_obj.selectData("r_id", GeneralParameters.rest_table,
                                   "r_datetime = to_date('" + str(this_mouth_date) + "','yyyy-mm-dd hh24:mi:ss')"):
            print "rest_table 中 已存在该日期 资料"
            print "---Finished insert_rest_table!!"
            logging.info("End insertRest: insert_rest_table is already exist!!")
            self.writeTxt("insert Rest调休", "资料已存在，不需写入数据库")
            return

        # 获取在职员工的 工号
        human_all = self.dml_obj.selectData('e_id', GeneralParameters.employee_table, "e_status='%s'" % u'在職')

        human_base_all = []
        for row_man in human_all:
            # 获取该员工上一个月的 g1 g2 g3 加班有效时数
            over_hours_str = 'h_32,h_33,h_34'
            over_hours_sql = "eemployee_id='%s' and h_yearmouth = to_date('%s','yyyy-mm-dd hh24:mi:ss')" % (
                row_man[0], str(prior_now_date))
            over_hours_obj = self.dml_obj.selectData(over_hours_str, GeneralParameters.over_hours_table, over_hours_sql)
            if over_hours_obj:
                g1_over_hours = over_hours_obj[0][0]
                g2_over_hours = over_hours_obj[0][1]
                g3_over_hours = over_hours_obj[0][2]
            else:
                g1_over_hours = 0
                g2_over_hours = 0
                g3_over_hours = 0

            # 获取 该员工 [上个月一号 到 这个月一号] 在‘工作日’的刷卡信息
            crd_where_sql = "c_lastcard is not null" + \
                            " and eemployee_id = '%s'" % row_man[0] + \
                            " and c_datetype = '%s'" % u'工作日' + \
                            " and c_datetime >= to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss')" + \
                            " and c_datetime < to_date('" + str(now_date) + "','yyyy-mm-dd hh24:mi:ss')"
            crd_str = 'eemployee_id,c_datetime,c_firstcrad,c_closedcard,c_lastcard,c_workcrad,c_code'
            crd_work = self.dml_obj.selectData(crd_str, GeneralParameters.crd_table, crd_where_sql)

            # 计算
            duty_work_time_g1 = timedelta(hours=0)
            for crd_row in crd_work:
                day_duty_work_time = self.getDutyWorkTimeMonth(crd_row, 'G1', prior_now_date)
                duty_work_time_g1 += day_duty_work_time

            duty_work_time_g1 = self.timedeltaToInteger(duty_work_time_g1)

            crd_sat_sql = "c_lastcard is not null" + \
                          " and c_firstcrad is not null" + \
                          " and eemployee_id = '%s'" % row_man[0] + \
                          " and c_datetype = '%s'" % u'周休日' + \
                          " and c_datetime >= to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss')" + \
                          " and c_datetime < to_date('" + str(now_date) + "','yyyy-mm-dd hh24:mi:ss')"
            duty_work_time_g2 = timedelta(hours=0)
            crd_sat = self.dml_obj.selectData(crd_str, GeneralParameters.crd_table, crd_sat_sql)
            for crd_s in crd_sat:
                if crd_s[1].weekday() == 5:
                    # 获取义务工作时数
                    get_duty_work_time = self.getDutyWorkTimeMonth(crd_s, 'G2', prior_now_date)
                    duty_work_time_g2 += get_duty_work_time

            # 转换数据格式
            duty_work_time_g2 = self.timedeltaToInteger(duty_work_time_g2)

            # 获取 g1,g2调休时数
            rest_time_g1, rest_time_g2 = self.rest_time(duty_work_time_g1, duty_work_time_g2)
            total_rest = rest_time_g1 + rest_time_g2

            # 获取 该员工 [上个月一号 到 这个月一号] 在‘晚班’的刷卡信息
            night_sql = "c_lastcard is not null" + \
                        " and eemployee_id = '%s'" % row_man[0] + \
                        " and c_type = '%s'" % u'晚班' + \
                        " and c_datetime >= to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss')" + \
                        " and c_datetime < to_date('" + str(now_date) + "','yyyy-mm-dd hh24:mi:ss')"
            nights_list = self.dml_obj.selectData('c_datetime', GeneralParameters.crd_table, night_sql)
            nights_num = len(nights_list)

            # 写进 db 时， 需要的 数组格式 [[],[],[],....]
            human_row_list = [this_mouth_date, row_man[0], g1_over_hours, duty_work_time_g1,
                              rest_time_g1, g2_over_hours, duty_work_time_g2, rest_time_g2,
                              g3_over_hours, nights_num, total_rest]

            human_base_all.append(human_row_list)

        if human_base_all:
            self.insertExcept(human_base_all, GeneralParameters.rest_order_string, GeneralParameters.rest_table,
                              "insert Rest调休")
        else:
            self.writeTxt("insert Rest调休", "没有计算出数据")
        self.writeTxt("insert Rest调休", "Finished")
        print "---Finished insertTimeout!!"
        logging.info("End insertRest!!")

    @staticmethod
    def rest_time(g1_hours, g2_hours):
        """
        @note: 调休公式 计算
        :param g1_hours:
        :param g2_hours:
        :return: 得到 g1,g2调休时数
        """
        rest_g1 = 0
        rest_g2 = 0
        g2_to_g1 = 0
        if g1_hours < 28:
            if g2_hours < 4:
                g2_to_g1 = 0
                rest_g2 = 0
            elif g2_hours > 8:
                g2_to_g1 = 0
                rest_g2 = 8
            else:
                rest_g2 = int(g2_hours)
        else:
            if g2_hours < 4:
                g2_to_g1 = g2_hours
            elif g2_hours > 8:
                g2_to_g1 = g2_hours - 8
                rest_g2 = 8
            else:
                rest_g2 = int(g2_hours)

        all_time_g1 = g1_hours + g2_to_g1
        if all_time_g1 < 28:
            rest_g1 = 0
        elif 28 <= all_time_g1 < 36:
            rest_g1 = 4
        elif 36 <= all_time_g1 < 44:
            rest_g1 = 8
        elif 44 <= all_time_g1 < 52:
            rest_g1 = 12
        elif 52 <= all_time_g1 < 60:
            rest_g1 = 16
        elif 60 <= all_time_g1 < 68:
            rest_g1 = 20
        elif 68 <= all_time_g1 < 76:
            rest_g1 = 24
        elif 76 <= all_time_g1 < 84:
            rest_g1 = 28
        elif 84 <= all_time_g1 < 92:
            rest_g1 = 32
        elif 92 <= all_time_g1 < 100:
            rest_g1 = 36
        elif all_time_g1 >= 100:
            rest_g1 = 36
        return rest_g1, rest_g2

    @staticmethod
    def timedeltaToInteger(time_d):
        """
        :return: timedelta 转 float
        """
        time_int = str(time_d.total_seconds())
        time_int = float(time_int) / 3600
        time_int = round(time_int, 3)
        return time_int

    def getDutyWorkTimeMonth(self, crd_row, date_type, prior_now_date):
        """
        @note: 根据该员工 上个月那一天 的有效加班时数，来获取义务工作时数
        @note: crd_row :
        @note: 'eemployee_id,c_datetime,c_firstcrad,c_closedcard,c_lastcard,c_workcrad,c_code'
        """
        over_hours_days = ['h_01', 'h_02', 'h_03', 'h_04', 'h_05',
                           'h_06', 'h_07', 'h_08', 'h_09', 'h_10',
                           'h_11', 'h_12', 'h_13', 'h_14', 'h_15',
                           'h_16', 'h_17', 'h_18', 'h_19', 'h_20',
                           'h_21', 'h_22', 'h_23', 'h_24', 'h_25',
                           'h_26', 'h_27', 'h_28', 'h_29', 'h_30', 'h_31']
        for one_day in over_hours_days:
            if crd_row[1].day == int(one_day.split('_')[1]):
                db_day_str = one_day
                break

        # 获取该员工 上个月那一天 的有效加班时数 effectively_hours
        oh_where_sql = "h_yearmouth = to_date('%s','yyyy-mm-dd hh24:mi:ss') and eemployee_id = '%s'" % (
            str(prior_now_date), crd_row[0])
        over_hours_l = self.dml_obj.selectData(db_day_str, GeneralParameters.over_hours_table, oh_where_sql)

        if not over_hours_l:
            return timedelta(hours=0)
        else:
            effectively_hours = over_hours_l[0][0]

        # 根据 员工的工号以及班别，获取该班别的 ‘中午吃饭时间和晚上吃饭时间’
        lunch_rest_time, dinner_rest_time = self.getAttendanceRestTime(crd_row[0], crd_row[6])

        # crd_row[1],刷卡日期
        date_str = crd_row[1].strftime("%Y-%m-%d")

        # crd_row[5],規定上班時間
        work_card_time = datetime.strptime(date_str + ' ' + crd_row[5], '%Y-%m-%d %H:%M')

        # crd_row[3],規定下班時間
        set_crd_time = datetime.strptime(date_str + ' ' + crd_row[3], '%Y-%m-%d %H:%M')
        if set_crd_time < work_card_time:
            set_crd_time = set_crd_time + timedelta(days=1)

        if date_type == 'G1':
            # crd_row[4],下班刷卡時間
            reality_crd_time = crd_row[4]
            if effectively_hours > 0:
                if reality_crd_time > (set_crd_time + timedelta(hours=effectively_hours) + dinner_rest_time):
                    return reality_crd_time - (set_crd_time + timedelta(hours=effectively_hours)) - dinner_rest_time
            else:
                if reality_crd_time > set_crd_time:
                    return reality_crd_time - set_crd_time
        else:
            card_1 = work_card_time + timedelta(hours=4)
            card_2 = work_card_time + timedelta(hours=4) + lunch_rest_time
            # crd_row[2],上班刷卡時間
            if crd_row[2] < card_1:
                reality_crd_g2 = work_card_time if work_card_time > crd_row[2] else crd_row[2]
            elif crd_row[2] < set_crd_time:
                reality_crd_g2 = card_2 if card_2 > crd_row[2] else crd_row[2]
            else:
                if crd_row[2] > (set_crd_time + dinner_rest_time):
                    reality_crd_g2 = crd_row[2]
                else:
                    reality_crd_g2 = set_crd_time + dinner_rest_time

            if crd_row[2] < card_1:
                if crd_row[4] > (set_crd_time + dinner_rest_time):
                    work_time = crd_row[4] - reality_crd_g2 - lunch_rest_time - dinner_rest_time
                elif crd_row[4] > card_2:
                    work_time = crd_row[4] - reality_crd_g2 - lunch_rest_time
                else:
                    work_time = crd_row[4] - reality_crd_g2
            else:
                work_time = crd_row[4] - reality_crd_g2

            if work_time > timedelta(hours=effectively_hours):
                return work_time - timedelta(hours=effectively_hours)

        return timedelta(hours=0)

    def insertDutyWork(self):
        """
        @note: 超時加班(義務)
        """
        self.file_object.write("\n ---------------------DutyWork 义务加班时数----------------------- \n")
        self.writeTxt("insert DutyWork义务加班时数", "Beginning")
        # 获取日期 这个月年份和月份   上个月年份和月份
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()
        # 把日期格式的string 转化成 datetime
        db_need_date = self.getNewDate(prior_year, prior_mouth, "05")
        print db_need_date
        # 存在判定
        if self.dml_obj.selectData("d_id", GeneralParameters.duty_work_table,
                                   "d_datetime = to_date('" + str(db_need_date) + "','yyyy-mm-dd hh24:mi:ss')"):
            print " duty_work_table 中 已存在该日期 资料"
            print "---Finished insert duty_work_table!!"
            logging.info("End insertDutyWork: duty_work_table is already exist!!")
            self.writeTxt("insert DutyWork义务加班时数", "资料已存在，不需写入数据库")
            return

        # 通过SQL语句，在 員工考勤中提取 [上个月] 员工的考勤信息
        crd_where_sql = "a_datetime = to_date('" + str(db_need_date) + "','yyyy-mm-dd hh24:mi:ss') order by a_datetime"
        #                                    员工工号   部长英文名    總工作時長       平均義務時長
        duty_tup = self.dml_obj.selectData("a_employee,a_leader,a_totaldutyhours,a_avgdutyhours",
                                           # eattendance # 員工考勤
                                           GeneralParameters.attendance_table, crd_where_sql)

        # 统计，各个主管下的员工义务加班时数
        duty_dic = {}
        # 遍历上个月的考勤信息
        for each_list in duty_tup:
            # 处长跳过
            if each_list[1] == 'Magma':
                continue
            # 存入字典 部长英文名为key
            if each_list[1] not in duty_dic.keys():
                duty_dic[each_list[1]] = [each_list[2]]  # 總工作時長
            else:
                duty_dic[each_list[1]].append(each_list[2])

        # 写进 db 时， 需要的 数组格式 [[],[],[],....]
        insert_duty_data = []
        for leader, _list in duty_dic.items():
            total_duty = 0
            # 遍历總工作時長值
            for each_data in _list:
                total_duty = total_duty + each_data
            # 统计超時加班人/次
            duty_work_ave = total_duty / len(_list)
            # 四舍五入
            duty_work_ave = round(duty_work_ave, 1)
            #                     上个月五号           超時加班人/次     總工作時長值个数==該主管下的常設師級人數
            each_insert_data = [db_need_date, leader, duty_work_ave, len(_list)]
            insert_duty_data.append(each_insert_data)
            print "each_insert_data:", each_insert_data, len(_list), type(len(_list))

        # 数据库插入
        if insert_duty_data:
            self.insertExcept(insert_duty_data, GeneralParameters.duty_work_order_string,
                              GeneralParameters.duty_work_table, "insert DutyWork义务加班时数")
        else:
            self.writeTxt("insert DutyWork义务加班时数", "没有计算出数据")
        self.writeTxt("insert DutyWork义务加班时数", "Finished")
        logging.info("End insertDutyWork!!")

    def insertSectionDutyWork(self):
        """
        @note: 超時加班(義務) 科级
        """
        self.file_object.write("\n ---------------------SectionDutyWork 义务加班时数----------------------- \n")
        self.writeTxt("insert SectionDutyWork义务加班时数", "Beginning")
        # 获取日期 这个月年份和月份   上个月年份和月份
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()
        # 把日期格式的string 转化成 datetime
        db_need_date = self.getNewDate(prior_year, prior_mouth, "05")
        print db_need_date
        # 存在判定
        if self.dml_obj.selectData("d_id", GeneralParameters.section_work_table,
                                   "d_datetime = to_date('" + str(db_need_date) + "','yyyy-mm-dd hh24:mi:ss')"):
            print " Section_duty_work_table 中 已存在该日期 资料"
            print "---Finished insert Section_duty_work_table!!"
            logging.info("End insertSectionDutyWork: Section_duty_work_table is already exist!!")
            self.writeTxt("insert SectionDutyWork义务加班时数", "资料已存在，不需写入数据库")
            return

        # 通过SQL语句，在 員工考勤中提取 [上个月] 员工的考勤信息
        crd_where_sql = "a_datetime = to_date('" + str(db_need_date) + "','yyyy-mm-dd hh24:mi:ss') order by a_datetime"
        #                                    员工工号   部长英文名    總工作時長       平均義務時長
        duty_tup = self.dml_obj.selectData("a_employee,a_leader,a_totaldutyhours,a_avgdutyhours",
                                           # eattendance # 員工考勤
                                           GeneralParameters.attendance_table, crd_where_sql)
        # 部级id
        Ministerial = self.dml_obj.selectData("d_leadernum",
                                              GeneralParameters.department_table)
        # 部级id列表
        Ministerial_list = []
        for i in Ministerial:
            Ministerial_list.append(i[0])
        # 科级id
        Section = self.dml_obj.selectData("s_id",
                                          GeneralParameters.subject_table)

        # 统计，各个科级下的员工义务加班时数
        duty_dic = {}
        # 遍历上个月的考勤信息
        for each_list in duty_tup:
            # 处长跳过
            if each_list[1] == 'Magma':
                continue
            # 部长跳过
            if each_list[0] in Ministerial_list:
                continue
            # 获取员工对应的科级英文名
            sql_str = " '" + str(each_list[0]) + "'= e_id"
            Section_id = self.dml_obj.selectData("e_id, e_functionteam, edepartment_id",
                                                 GeneralParameters.employee_table, sql_str)

            # 存入字典 科长英文名 为key
            if Section_id[0][1] not in duty_dic.keys():
                duty_dic[Section_id[0][1]] = [each_list[2]]  # 總工作時長
            else:
                duty_dic[Section_id[0][1]].append(each_list[2])

        # 写进 db 时， 需要的 数组格式 [[],[],[],....]
        insert_duty_data = []
        for leader, _list in duty_dic.items():
            total_duty = 0
            # 遍历總工作時長值
            for each_data in _list:
                total_duty = total_duty + each_data
            # 统计超時加班人/次
            duty_work_ave = total_duty / len(_list)
            # 四舍五入
            duty_work_ave = round(duty_work_ave, 1)
            # 获取部级领导名
            sql_str = " '" + str(leader) + "'= e_functionteam"
            leader_name_list = self.dml_obj.selectData("e_leader",
                                                       GeneralParameters.employee_table, sql_str)
            leader_name = list(set(leader_name_list))
            # 获取员工对应的科级英文名
            #                     上个月五号           超時加班人/次     總工作時長值个数==該主管下的常設師級人數
            each_insert_data = [db_need_date, leader, duty_work_ave, len(_list), leader_name[0][0]]
            insert_duty_data.append(each_insert_data)
            print "each_insert_data:", each_insert_data, len(_list), type(len(_list))

        # 数据库插入
        if insert_duty_data:
            self.insertExcept(insert_duty_data, GeneralParameters.section_work_order_string,
                              GeneralParameters.section_work_table, "insert SectionDutyWork义务加班时数")
        else:
            self.writeTxt("insert SectionDutyWork义务加班时数", "没有计算出数据")
        self.writeTxt("insert SectionDutyWork义务加班时数", "Finished")
        logging.info("End insertSectionDutyWork!!")

    def New_getCrdData(self):
        """
        @note: 常设师级员工的刷卡记录
        """
        # 获得 日期
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()
        prior_now_date = self.getNewDate(prior_year, prior_mouth, "01")
        now_date = self.getNewDate(this_year, this_mouth, "01")
        # 测试
        # prior_now_date = self.getNewDate('2018', '5', "01")
        # now_date = self.getNewDate('2018', '6', "01")
        # 通过SQL语句，在 刷卡信息中提取 [上个月一号 到 这个月一号] 的常设师级所有员工的刷卡记录
        crd_where_sql = "(c_datetype='" + u"工作日" + \
                        "' or c_datetype='" + u"周休日" + \
                        "') and c_firstcrad is not null" + \
                        " and c_lastcard is not null " + \
                        " and c_datetime >= to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss')" + \
                        " and c_datetime < to_date('" + str(now_date) + "','yyyy-mm-dd hh24:mi:ss') order by c_datetime"
        unique_list = self.dml_obj.selectData(
            "eemployee_id,c_datetime,c_lastcard,c_code,c_type, c_firstcrad, c_datetype", GeneralParameters.crd_table,
            crd_where_sql)

        return unique_list

    @staticmethod
    def get_current_month_start_and_end(date):
        """
        年份 date(2017-09-08格式)
        :param date:
        :return:本月第一天日期和本月最后一天日期
        """
        if date.count('-') != 2:
            raise ValueError('- is error')
        year, month = str(date).split('-')[0], str(date).split('-')[1]
        end = calendar.monthrange(int(year), int(month))[1]
        start_date = '%s-%s-01' % (year, month)
        end_date = '%s-%s-%s' % (year, month, end)
        return start_date, end_date

    def RealTime_getCrdData(self):
        """
        @note: 常设师级员工的实时刷卡记录
        """
        # 获得 日期
        now_time_date = str(datetime.now()).split(" ")[0]
        now_time_tuple = self.get_current_month_start_and_end(now_time_date)
        prior_now_date = now_time_tuple[0]
        now_date = now_time_tuple[1]
        # 测试
        # prior_now_date = "2019-1-01"
        # now_date = "2019-1-31"

        # 一号获取上个月的数据
        if str(datetime.now()).split(" ")[0].split("-")[-1] in ["1", "01"]:
            #  年
            year_date = prior_now_date.split("-")[0]
            mouth_date = prior_now_date.split("-")[1]

            # 月也为1号
            if prior_now_date.split("-")[1] in ["1", "01"]:
                #  年 - 1
                year_date = str(int(year_date) - 1)
                # 月变12
                mouth_date = '12'
                #  拼接
                prior_now_date = "-".join((year_date, mouth_date, prior_now_date.split("-")[-1]))
                now_date = "-".join((year_date, mouth_date, now_date.split("-")[-1]))
            else:
                # 月减一
                mouth_date = str(int(mouth_date) - 1)
                #  拼接
                prior_now_date = "-".join((year_date, mouth_date, prior_now_date.split("-")[-1]))
                now_date = "-".join((year_date, mouth_date, now_date.split("-")[-1]))


        # 通过SQL语句，在 刷卡信息中提取 [上个月一号 到 这个月一号] 的常设师级所有员工的刷卡记录
        crd_where_sql = "(c_datetype='" + u"工作日" + \
                        "' or c_datetype='" + u"周休日" + \
                        "') and c_firstcrad is not null" + \
                        " and c_lastcard is not null " + \
                        " and c_datetime >= to_date('" + prior_now_date + "','yyyy-mm-dd hh24:mi:ss')" + \
                        " and c_datetime < to_date('" + now_date + "','yyyy-mm-dd hh24:mi:ss') order by c_datetime"
        unique_list = self.dml_obj.selectData(
            "eemployee_id,c_datetime,c_lastcard,c_code,c_type, c_firstcrad, c_datetype", GeneralParameters.lmf_crd_table,
            crd_where_sql)

        return unique_list

    def insertNightData(self):
        """
        @note: 人均晚班天次
        """
        self.file_object.write("\n ---------------------NightData 夜班----------------------- \n")
        self.writeTxt("insert NightData夜班", "Beginning")
        # 获得 今年今月
        # 获取日期 这个月年份和月份   上个月年份和月份
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()
        prior_now_date = self.getNewDate(prior_year, prior_mouth, "01")
        now_date = self.getNewDate(this_year, this_mouth, "01")
        # 把日期格式的string 转化成 datetime
        db_need_date = self.getNewDate(prior_year, prior_mouth, "05")
        # 存在判定
        if self.dml_obj.selectData("n_id", GeneralParameters.night_shift_table,
                                   "n_datetime = to_date('" + str(db_need_date) + "','yyyy-mm-dd hh24:mi:ss')"):
            print " 已存在 该日期资料"
            print "---Finished insert night_shift_table!!"
            logging.info("End insertNightData: night_shift_table is already exist!!")
            self.writeTxt("insert NightData夜班", "资料已存在，不需写入数据库")
            return

        # 通过SQL语句，在 刷卡信息中提取 [上个月一号 到 这个月一号] 的常设师级员工的刷卡记录
        crd_where_sql = "c_type='" + u"晚班" + "'" + \
                        " and c_datetype !='" + u"節假日" + "'" + \
                        " and c_firstcrad is not null and c_lastcard is not null" + \
                        " and c_datetime >= to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss')" + \
                        " and c_datetime < to_date('" + str(now_date) + "','yyyy-mm-dd hh24:mi:ss') order by c_datetime"
        all_employee_list = self.dml_obj.selectData("eemployee_id", GeneralParameters.crd_table, crd_where_sql)
        date_time = db_need_date
        night_shift_data = []

        leaders = self.getLeaderNames()
        leader_dic = collections.defaultdict(list)

        for row in all_employee_list:
            # 工号
            this_man_id = row[0]
            # 只要师级 常设
            exist_flag = self.getEmployeeExist(this_man_id)
            if exist_flag:
                # 部级英文名
                leader_name = self.getLeaderForId(row[0])
                leader_dic[leader_name].append(row[0])

        # 写进 db 时， 需要的 数组格式 [[],[],[],....]
        for leader_name in leaders:
            # 根据 e_leader 获取该主管下有多少人
            group_all_number = self.getGroupNumber(leader_name[0], prior_now_date, now_date)  # 计算平均人均晚班天次
            num_ = len(leader_dic[leader_name[0]]) / float(group_all_number)
            night_num = round(num_, 1)
            night_shift_row_list = [date_time, leader_name[0], night_num]
            night_shift_data.append(night_shift_row_list)
            print "night_shift_row_list:", night_shift_row_list

        self.insertExcept(night_shift_data, GeneralParameters.night_shift_order_string,
                          GeneralParameters.night_shift_table, "insert NightData夜班")
        self.writeTxt("insert LeaveNum夜班", "Finished")
        print "---- Finished insertNightData"
        logging.info("End insertNightData!!")

    def insertSectionNightData(self):
        """
        @note: 人均晚班天次--科级
        """
        self.file_object.write("\n ---------------------SectionNightData 夜班----------------------- \n")
        self.writeTxt("insert SectionNightData夜班", "Beginning")
        # 获得 今年今月
        # 获取日期 这个月年份和月份   上个月年份和月份
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()
        prior_now_date = self.getNewDate(prior_year, prior_mouth, "01")
        now_date = self.getNewDate(this_year, this_mouth, "01")
        # 把日期格式的string 转化成 datetime
        db_need_date = self.getNewDate(prior_year, prior_mouth, "05")
        print prior_now_date, "---->", now_date
        # 存在判定
        if self.dml_obj.selectData("n_id", GeneralParameters.section_night_shift_table,
                                   "n_datetime = to_date('" + str(db_need_date) + "','yyyy-mm-dd hh24:mi:ss')"):
            print " 已存在 该日期资料"
            print "---Finished insert section_night_shift_table!!"
            logging.info("End insertSectionNightData: section_night_shift_table is already exist!!")
            self.writeTxt("insert SectionNightData夜班", "资料已存在，不需写入数据库")
            return

        # 通过SQL语句，在 刷卡信息中提取 [上个月一号 到 这个月一号] 的常设师级员工的刷卡记录
        crd_where_sql = "c_type='" + u"晚班" + "'" + \
                        " and c_datetype !='" + u"節假日" + "'" + \
                        " and c_firstcrad is not null and c_lastcard is not null" + \
                        " and c_datetime >= to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss')" + \
                        " and c_datetime < to_date('" + str(now_date) + "','yyyy-mm-dd hh24:mi:ss') order by c_datetime"
        all_employee_list = self.dml_obj.selectData("eemployee_id", GeneralParameters.crd_table, crd_where_sql)
        date_time = db_need_date
        night_shift_data = []

        # 所有科级名
        leaders = self.getSectionNames()
        leader_dic = collections.defaultdict(list)

        for row in all_employee_list:
            this_man_id = row[0]
            # 只要师级 常设
            exist_flag = self.getEmployeeExist(this_man_id)
            if exist_flag:
                leader_name = self.getSectionForId(row[0])
                leader_dic[leader_name].append(row[0])

        # 写进 db 时， 需要的 数组格式 [[],[],[],....]
        for leader_name in leaders:
            #  获取该科级下有多少人
            group_all_number = self.getSectionGroupNumber(leader_name[0], prior_now_date, now_date)
            # 计算平均人均晚班天次
            num_ = len(leader_dic[leader_name[0]]) / float(group_all_number)
            night_num = round(num_, 1)
            night_shift_row_list = [date_time, leader_name[0], night_num]
            night_shift_data.append(night_shift_row_list)
            print "night_shift_row_list:", night_shift_row_list

        self.insertExcept(night_shift_data, GeneralParameters.section_night_shift_order_string,
                          GeneralParameters.section_night_shift_table, "insert SectionNightData夜班")
        self.writeTxt("insert SectionLeaveNum夜班", "Finished")
        print "---- Finished insertSectionNightData"
        logging.info("End insertSectionNightData!!")

    def getLeaderNames(self):
        """
        @note: 获取 有英文名字的 主管
        """
        leader_names = self.dml_obj.selectData("e_ename", GeneralParameters.employee_table, "e_ename is not null")
        return leader_names

    def getSectionNames(self):
        """
        @note: 获取 有英文名的 科级
        """
        section_names = self.dml_obj.selectData("e_functionteam", GeneralParameters.employee_table,
                                                "e_functionteam is not null and e_functionteam != 'Magma'")
        section_names = list(set(section_names))
        return section_names

    def getGroupNumber(self, leader_name, prior_now_date, now_date):
        """
        @note: 根据 e_leader 获取该主管下有多少人
        """
        group_sql_where = "e_status = '" + u"在職" + "'" + \
                          " and e_grade like '%" + u"師" + "%' and e_category='" + u"常設" + "'" + \
                          " and e_leader = '" + leader_name + "'"
        group_number = self.dml_obj.selectData("e_id", GeneralParameters.employee_table,
                                               group_sql_where)
        return len(group_number)

    def getSectionGroupNumber(self, section_name, prior_now_date, now_date):
        """
        @note: 根据 e_leader 获取该科级下有多少人
        """
        group_sql_where = "e_status = '" + u"在職" + "'" + \
                          " and e_grade like '%" + u"師" + "%' and e_category='" + u"常設" + "'" + \
                          " and e_functionteam = '" + section_name + "'"
        group_number = self.dml_obj.selectData("e_id", GeneralParameters.employee_table,
                                               group_sql_where)
        return len(group_number)

    def insertGreaterThanData(self):
        """
        部级
        @note: 大於某點人次
        @note: [>9, >9.5, >10, >10.5, >11, >11.5, >12, >12.5]
        """
        self.file_object.write("\n ---------------------GreaterThanData 工作时长超过几小时----------------------- \n")
        self.writeTxt("insert GreaterThanData工作时长超过几小时", "Beginning")
        # 获得 今年今月  
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()

        # 判断 数据库中 是否存在该月数据 避免重复插入
        db_need_date = self.getNewDate(prior_year, prior_mouth, "05")
        # 测试
        # db_need_date = self.getNewDate('2018', '5', "05")

        sql_where = "g_datetime=to_date('" + str(db_need_date) + "','yyyy-mm-dd hh24:mi:ss')"
        db_datetime_tup = self.dml_obj.selectData("g_id", GeneralParameters.greater_than_table, sql_where)
        if db_datetime_tup:
            print " 已存在 该日期资料"
            print "---Finished insert greater_than_table!!"
            logging.info("End insertGreaterThanData: greater_than_table is already exist!!")
            self.writeTxt("insert GreaterThanData工作时长超过几小时", "资料已存在，不需写入数据库")
            return

        # 常设师级员工的刷卡记录
        crd_data = self.New_getCrdData()
        dic_data = {}
        dic_personal_data = {}
        date_time = db_need_date

        greater_than_data = []
        personal_than_data = []
        for row in crd_data:
            # [eemployee_id,c_datetime,c_lastcard]
            # 工号
            this_man_id = row[0]
            # 只要师级常设
            exist_flag = self.getEmployeeExist(this_man_id)
            if exist_flag:
                leader_name = self.getLeaderForId(row[0])
                if leader_name == 'Magma':
                    continue
                # 个人
                if row[0] not in dic_personal_data.keys():
                    dic_personal_data[this_man_id] = [this_man_id, leader_name, 0, 0, 0, 0, 0, 0, 0, 0]
                # 部级
                if leader_name not in dic_data.keys():
                    dic_data[leader_name] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                # 计算人数
                time_list = ['9:00:00', '9:30:00', '10:00:00', '10:30:00', '11:00:00', '11:30:00', '12:00:00',
                             '12:30:00']
                # 获取是否加班 和 工作小时数
                t_index, overtime_bool = self.ga_analysisTime(row, time_list)

                # 异常数据过滤
                if t_index == 999:
                    continue

                # 是否加班了
                if overtime_bool:
                    # 非准点下班 加一
                    dic_data[leader_name][1] += 1
                else:
                    # 准点下班 加一
                    dic_data[leader_name][0] += 1

                # 工作时长没有超过9小时,略过
                if t_index == 100:
                    continue
                # 工作时超过9小时
                for i in range(2, t_index + 3):
                    dic_data[leader_name][i] += 1
                # 个人
                for j in range(2, t_index + 3):
                    dic_personal_data[this_man_id][j] += 1

        for k, v in dic_data.items():
            row_data = [date_time, k]
            # 在个人考勤资料中获取各主管下的 [a_offduty,a_unoffduty]
            offDutyTotal = 0
            unOffDutyTotal = 0
            attendance_sql = "a_leader = '" + k + \
                             "' and a_datetime = to_date('" + str(date_time) + "', 'yyyy-mm-dd hh24:mi:ss')"
            attendance_tup = self.dml_obj.selectData("a_offduty,a_unoffduty", GeneralParameters.attendance_table,
                                                     attendance_sql)
            for each_tup in attendance_tup:
                offDutyTotal += each_tup[0]
                unOffDutyTotal += each_tup[1]
            v[0] = offDutyTotal
            v[1] = unOffDutyTotal
            row_data.extend(v)
            greater_than_data.append(row_data)
            print "row_data:", row_data

        self.insertExcept(greater_than_data, GeneralParameters.greater_than_order_string,
                          GeneralParameters.greater_than_table, "insert GreaterThanData大于几点")
        self.writeTxt("insert GreaterThanData工作时长超过几小时", "Finished")
        logging.info("End insertGreaterThanData!!")

        for personal in dic_personal_data.values():
            personal.insert(0, date_time)
            personal_than_data.append(personal)

        self.insertExcept(personal_than_data, GeneralParameters.personal_work_time_string,
                          GeneralParameters.personal_work_time_table, "insert PersonalWorkTime超过几小时")
        self.writeTxt("insert PersonalWorkTime工作时长超过几小时", "Finished")
        logging.info("End insertPersonalWorkTime!!")

    def insertSectionGreaterThanData(self):
        """
        科级
        @note: 大於某點人次
        @note: [>9, >9.5, >10, >10.5, >11, >11.5, >12, >12.5]
        """
        self.file_object.write("\n ---------------------SectionGreaterThanData 工作时长超过几小时----------------------- \n")
        self.writeTxt("insert SectionGreaterThanData大于几点", "Beginning")
        # 获得 今年今月
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()

        # 判断 数据库中 是否存在该月数据 避免重复插入
        db_need_date = self.getNewDate(prior_year, prior_mouth, "05")
        # 测试
        # db_need_date = self.getNewDate('2019', '7', "05")

        sql_where = "g_datetime=to_date('" + str(db_need_date) + "','yyyy-mm-dd hh24:mi:ss')"
        db_datetime_tup = self.dml_obj.selectData("g_id", GeneralParameters.section_greater_than_table, sql_where)
        if db_datetime_tup:
            print " 已存在 该日期资料"
            print "---Finished insert section_greater_than_table!!"
            logging.info("End insertSectionGreaterThanData: section_greater_than_table is already exist!!")
            self.writeTxt("insert GreaterSectionThanData工作时长超过几小时", "资料已存在，不需写入数据库")
            return

        # 常设师级员工的刷卡记录
        crd_data = self.New_getCrdData()
        dic_data = {}
        date_time = db_need_date

        greater_than_data = []
        for row in crd_data:
            # [eemployee_id,c_datetime,c_lastcard]
            this_man_id = row[0]
            # 只要师级常设
            exist_flag = self.getEmployeeExist(this_man_id)
            if exist_flag:
                section_name = self.getSectionForId(row[0])
                # 去除处长
                if section_name == 'Magma':
                    continue
                if section_name not in dic_data.keys():
                    dic_data[section_name] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                # 计算人数
                time_list = ['9:00:00', '9:30:00', '10:00:00', '10:30:00', '11:00:00', '11:30:00', '12:00:00',
                             '12:30:00']
                # 获取是否加班 和 工作小时数
                t_index, overtime_bool = self.ga_analysisTime(row, time_list)

                # 异常数据过滤
                if t_index == 999:
                    continue

                # 是否加班了
                if overtime_bool:
                    # 非准点下班 加一
                    dic_data[section_name][1] += 1
                else:
                    # 准点下班 加一
                    dic_data[section_name][0] += 1

                # 工作时长没有超过9小时,略过
                if t_index == 100:
                    continue
                # 工作时超过9小时
                for i in range(2, t_index + 3):
                    dic_data[section_name][i] += 1

        for k, v in dic_data.items():
            row_data = [date_time, k]
            # 在个人考勤资料中获取各科级下的 [a_offduty,a_unoffduty]
            offDutyTotal = 0
            unOffDutyTotal = 0
            # 先找到该时间下的所有attendance的所有员工
            attendance_sql = "a_datetime = to_date('" + str(date_time) + "', 'yyyy-mm-dd hh24:mi:ss')"
            #                                          员工工号   准点下班天数  非准点下班天数
            attendance_tup = self.dml_obj.selectData("a_employee,a_offduty,a_unoffduty",
                                                     GeneralParameters.attendance_table, attendance_sql)

            attendance_list = []
            for each_tup in attendance_tup:
                # 通过获取的 id 去eeployee表中找科级名是否和 k值得相同
                # group_sql_where = "e_status = '" + u"在職" + "'" + \
                #                   " and e_grade like '%" + u"師" + "%' and e_category='" + u"常設" + "'" + \
                #                   " and e_id = '" + each_tup[0] + "'"
                group_sql_where = " e_id = '" + each_tup[0] + "'"
                try:
                    group_functionteam = self.dml_obj.selectData("e_functionteam", GeneralParameters.employee_table,
                                                                 group_sql_where)
                except:
                    continue

                # 判断是否是该科级
                if group_functionteam[0][0] == k:
                    # 是的话添加
                    attendance_list.append(each_tup)

            for each_data in attendance_list:
                offDutyTotal += each_data[1]
                unOffDutyTotal += each_data[2]
            v[0] = offDutyTotal
            v[1] = unOffDutyTotal
            row_data.extend(v)
            greater_than_data.append(row_data)
            print "row_data:", row_data

        self.insertExcept(greater_than_data, GeneralParameters.section_greater_than_order_string,
                          GeneralParameters.section_greater_than_table, "insert SectionGreaterThanData工作时长超过几小时")
        self.writeTxt("insert SectionGreaterThanData工作时长超过几小时", "Finished")
        logging.info("End insertSectionGreaterThanData!!")


    def insertLmfPersonalWorkTime(self):
        """
        个人--实时
        @note: 工作时长超过几小时
        @note: [>9, >9.5, >10, >10.5, >11, >11.5, >12, >12.5]
        """
        self.file_object.write("\n ---------------------LmfPersonalWorkTime工作时长超过几小时----------------------- \n")
        self.writeTxt("insert LmfPersonalWorkTime超过几小时", "Beginning")

        # 获得 今年今月
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()
        # 测试
        # this_year, this_mouth, prior_year, prior_mouth = ("2019", "10", "2019", "09")

        # 判断 数据库中 是否存在该月数据 避免重复插入
        db_need_date = self.getNewDate(this_year, this_mouth, "05")

        lmf_crd_where_sql = "group by c_datetime order by c_datetime desc"
        time_list = self.dml_obj.selectData("c_datetime", GeneralParameters.lmf_crd_table + " " + lmf_crd_where_sql)
        new_year_month = time_list[0][0]
        new_year = new_year_month.year
        new_month = new_year_month.month

        # 一号删除上个月的
        if str(datetime.now()).split(" ")[0].split("-")[-1] in ["1", "01"]:
            new_year = new_year
            if new_month == 1:
                new_year = new_year - 1
                new_month = 12
            else:
                new_month = new_month - 1
        lmf_personal_work_time_sql = "P_DATETIME = to_date('%s-%s-05 00:00:00', 'yyyy-mm-dd hh24:mi:ss')" %(str(new_year), str(new_month))

        self.dml_obj.deleteData(GeneralParameters.lmf_personal_work_time_table, lmf_personal_work_time_sql)

        # 常设师级员工的实时刷卡记录
        crd_data = self.RealTime_getCrdData()
        date_time = db_need_date
        dic_personal_data = {}

        personal_than_data = []
        for row in crd_data:
            # [eemployee_id,c_datetime,c_lastcard]
            # 工号
            this_man_id = row[0]
            # 只要师级常设
            exist_flag = self.getEmployeeExist(this_man_id)
            if exist_flag:
                leader_name = self.getLeaderForId(row[0])
                if leader_name == 'Magma':
                    continue
                # 个人
                if row[0] not in dic_personal_data.keys():
                    dic_personal_data[this_man_id] = [this_man_id, leader_name, 0, 0, 0, 0, 0, 0, 0, 0]
                # 计算人数
                time_list = ['9:00:00', '9:30:00', '10:00:00', '10:30:00', '11:00:00', '11:30:00', '12:00:00',
                             '12:30:00']
                # 获取是否加班 和 工作小时数
                t_index, overtime_bool = self.ga_analysisTime(row, time_list)

                # 异常数据过滤
                if t_index == 999:
                    continue

                # 工作时长没有超过9小时,略过
                if t_index == 100:
                    continue
                # 工作时超过9小时
                # 个人
                for j in range(2, t_index + 3):
                    dic_personal_data[this_man_id][j] += 1

        for personal in dic_personal_data.values():
            personal.insert(0, date_time)
            personal_than_data.append(personal)

        self.insertExcept(personal_than_data, GeneralParameters.lmf_personal_work_time_string,
                          GeneralParameters.lmf_personal_work_time_table, "insert LmfPersonalWorkTime工作时长超过几小时")
        self.writeTxt("insert LmfPersonalWorkTime工作时长超过几小时", "Finished")
        logging.info("End insertLmfPersonalWorkTime工作时长超过几小时!!")
        
    def Z_T_classification(self, e_id):
        """判断中干和台干"""
        employee_sql = "e_id = '" + e_id + "'"
        classification = self.dml_obj.selectData("E_DIFFERENCE", GeneralParameters.employee_table, employee_sql)

        if classification[0][0] == '臺幹':
            return False

        return True

    def class_time(self, c_code, fist_time, last_time):
        """
            根据code查出班表算工作时长
            :return 真正工作时长, 加班开始时间+35分钟
        """
        class_sql = "c_code = '" + c_code + "'"
        class_data = self.dml_obj.selectData("C_TYPE, C_FIRSTUP, C_FIRSTDOWN, C_SECONDEUP, C_SECONDEDOWN, C_BEGINOVER",
                                             GeneralParameters.classes_table, class_sql)

        # 上班标准时间
        start_work_time = class_data[0][1]
        # 判断是否迟到打卡
        if fist_time > datetime.strptime(str(last_time).split(" ")[0] + " " + start_work_time, "%Y-%m-%d %H:%M"):
            # 迟到 获取真正上班时间
            start_work_time = str(fist_time).split(" ")[1][:-3]

        # 计算工作总时长  下班打卡时间 - 上班标准时间
        work_hours = last_time - datetime.strptime(str(last_time).split(" ")[0] + " " + start_work_time,
                                                   "%Y-%m-%d %H:%M")
        # 得到负数说明拼接的时间不对
        if work_hours.days < 0:
            # 判断是否迟到打卡
            if fist_time > datetime.strptime(str(fist_time).split(" ")[0] + " " + start_work_time, "%Y-%m-%d %H:%M"):
                # 迟到 获取真正上班时间
                start_work_time = str(fist_time).split(" ")[1][:-3]
            work_hours = last_time - datetime.strptime(str(fist_time).split(" ")[0] + " " + start_work_time,
                                                       "%Y-%m-%d %H:%M")
        # 休息时间
        fist_up = datetime.strptime(class_data[0][1], "%H:%M")
        fist_down = datetime.strptime(class_data[0][2], "%H:%M")
        second_up = datetime.strptime(class_data[0][3], "%H:%M")
        second_down = datetime.strptime(class_data[0][4], "%H:%M")
        # 加班标准时间
        beginover = datetime.strptime(class_data[0][5], "%H:%M")
        beginover35 = datetime.strptime(str(fist_time).split(" ")[0] + " " + class_data[0][5],
                                        "%Y-%m-%d %H:%M") + timedelta(minutes=35)

        # 判断上班时间是否跨天
        if (beginover - fist_up).days < 0:
            # 跨天了 加一天
            beginover35 += timedelta(days=1)

        fist_time_hours = second_up - fist_down
        # 跨天
        if fist_time_hours.days < 0:
            second_up = datetime.strptime(class_data[0][3], "%H:%M") + timedelta(days=1)
            fist_time_hours = second_up - fist_down

        second_time_hours = beginover - second_down
        # 跨天
        if second_time_hours.days < 0:
            # 加班标准时间
            beginover = datetime.strptime(class_data[0][5], "%Y-%m-%d %H:%M") + timedelta(days=1)
            second_time_hours = beginover - second_down

        #  真正工作时长= 工作总时长-休息时间
        work_hours_time = work_hours - (fist_time_hours + second_time_hours)

        return work_hours_time, beginover35

    def ga_analysisTime(self, row, time_list):
        """
        @note: 获取 last_time 在time_list中的元素位置,并返回工作时长和是否加班
        """
        last_time = row[2]
        code = row[3]
        fist_time = row[5]
        sunday = row[6]
        t_index = 100
        overtime_bool = False  # 默认准点下班

        # 台干
        if not self.Z_T_classification(row[0]):
            code = 'BC021'
            # 判断跨天
            work_time = last_time - fist_time
            if work_time.days < 0:
                # 加一天
                last_time += timedelta(days=1)
            work_hours_time, beginover35 = self.class_time(code, fist_time, last_time)

        else:

            # 陆干
            work_hours_time, beginover35 = self.class_time(code, fist_time, last_time)

        if work_hours_time < timedelta(minutes=1):
            # 异常数据 过滤
            t_index = 999
            return t_index, overtime_bool

        # 加班判断

        # 判断周休日--只属于加班
        if sunday == '周休日':
            overtime_bool = True  # 加班
        # 工作日
        elif last_time > beginover35:
            overtime_bool = True  # 加班

        # 工作超時判断
        # time_list = ['9:00:00', '9:30:00', '10:00:00', '10:30:00', '11:00:00', '11:30:00', '12:00:00', '12:30:00']
        i = 0
        j = 0
        for t in time_list:
            # 当前的满足不了,后面的也满足不了
            if i < j:
                break
            if datetime.strptime(str(work_hours_time), '%H:%M:%S') >= datetime.strptime(t, "%H:%M:%S"):
                t_index = time_list.index(t)
                i += 1
            j += 1
            # 第一个9点都不满足 跳出循环
            if not i:
                break

        return t_index, overtime_bool

    @staticmethod
    def analysisTime(last_time, time_list):
        """
        @note: 获取 last_time 在time_list中的元素位置
        """
        t_index = 100
        # time_list = ['18:00:00', '19:30:00', '20:00:00', '20:30:00', '21:00:00', '21:30:00', '22:00:00', '22:30:00', '23:00:00']
        lt_str = last_time.strftime("%H:%M:%S")

        for t in time_list:
            if datetime.strptime(lt_str, "%H:%M:%S") >= datetime.strptime(t, "%H:%M:%S"):
                t_index = time_list.index(t)
            if datetime.strptime('08:00:00', "%H:%M:%S") > datetime.strptime(lt_str, "%H:%M:%S"):
                t_index = 8
                break
        return t_index

    def getLeaderForId(self, employee_id):
        """
        @note: 获取每一个员工的 主管
        """
        if employee_id not in self.LeaderNameForId_dic.keys():
            leader_name = self.dml_obj.selectData("e_leader", GeneralParameters.employee_table,
                                                  "e_id = '" + employee_id + "'")
            self.LeaderNameForId_dic[employee_id] = leader_name[0][0]
        return self.LeaderNameForId_dic[employee_id]

    def getSectionForId(self, employee_id):
        """
        @note: 获取每一个员工的 科级名
        """
        if employee_id not in self.SectionNameForId_dic.keys():
            leader_name = self.dml_obj.selectData("e_functionteam", GeneralParameters.employee_table,
                                                  "e_id = '" + employee_id + "'")
            self.SectionNameForId_dic[employee_id] = leader_name[0][0]
        return self.SectionNameForId_dic[employee_id]

    def arrangeTimeoutData(self, all_data_dic):
        """
        @note: 整理从数据库中来的数据
        """
        time_over_str_list = ["09:00:00", "09:30:00", "10:00:00", "10:30:00", "11:00:00"]
        # 转化为时间格式
        time_over_time_list = [datetime.strptime(each_str, "%H:%M:%S") for each_str in time_over_str_list]

        timeout_data_dic = {}
        for key, value in all_data_dic.items():
            # 获取员工 leader
            leader_tup = self.dml_obj.selectData("e_leader", GeneralParameters.employee_table, "e_id='" + key + "'")
            this_leader_val = leader_tup[0][0]

            # 计算该员工 上月 平均超时 <type 'datetime.timedelta'>
            total_time = None
            for each_time in value:
                if total_time:
                    total_time = total_time + each_time
                else:
                    total_time = each_time
            avg_time = total_time / len(value)

            # 不能精确到小数点
            avg_time_str = str(avg_time).split(".")[0]
            this_list_num = self.getListNum(time_over_time_list, avg_time_str)
            if this_list_num is None:
                continue
            # 该员工的 avg_time 能得到 this_list_num，则算一个人次
            this_list_index = this_list_num + 1
            if this_leader_val not in timeout_data_dic.keys():
                this_value_list = [this_leader_val, 0, 0, 0, 0, 0]
                # 第一次 赋值
                this_value_list[this_list_index] = 1
                timeout_data_dic[this_leader_val] = this_value_list
            else:
                this_dic_value = timeout_data_dic[this_leader_val]
                this_dic_value[this_list_index] = this_dic_value[this_list_index] + 1

        return timeout_data_dic

    def arrangeSectionTimeoutData(self, all_data_dic):
        """
        @note: 整理从数据库中来的数据
        """
        time_over_str_list = ["09:00:00", "09:30:00", "10:00:00", "10:30:00", "11:00:00"]
        # 转化为时间格式
        time_over_time_list = [datetime.strptime(each_str, "%H:%M:%S") for each_str in time_over_str_list]

        timeout_data_dic = {}
        for key, value in all_data_dic.items():
            # 获取员工 科级名
            leader_tup = self.dml_obj.selectData("e_functionteam", GeneralParameters.employee_table,
                                                 "e_id='" + key + "'")
            this_leader_val = leader_tup[0][0]

            # 计算该员工 上月 平均超时 <type 'datetime.timedelta'>
            total_time = None
            for each_time in value:
                if total_time:
                    total_time = total_time + each_time
                else:
                    total_time = each_time
            avg_time = total_time / len(value)

            # 不能精确到小数点
            avg_time_str = str(avg_time).split(".")[0]
            this_list_num = self.getListNum(time_over_time_list, avg_time_str)
            if this_list_num is None:
                continue
            # 该员工的 avg_time 能得到 this_list_num，则算一个人次
            this_list_index = this_list_num + 1
            if this_leader_val not in timeout_data_dic.keys():
                this_value_list = [this_leader_val, 0, 0, 0, 0, 0]
                # 第一次 赋值
                this_value_list[this_list_index] = 1
                timeout_data_dic[this_leader_val] = this_value_list
            else:
                this_dic_value = timeout_data_dic[this_leader_val]
                this_dic_value[this_list_index] = this_dic_value[this_list_index] + 1

        return timeout_data_dic

    def getTimeoutData(self, crd_where_sql):
        """
        @note:  从数据库中获取 前一个月的 刷卡 数据
        """
        unique_tup = self.dml_obj.selectData(
            "eemployee_id,c_datetime,c_workcrad,c_firstcrad,c_closedcard,c_lastcard,c_code",
            GeneralParameters.crd_table,
            crd_where_sql)

        all_data_dic = {}
        for each_tup in unique_tup:
            this_man_id = each_tup[0]
            # this_datetime = each_tup[1]
            this_work_card = each_tup[2]
            this_first_card = each_tup[3]
            # this_closed_card = each_tup[4]
            this_last_card = each_tup[5]
            this_code = each_tup[6]
            # 只要师级常设
            exist_flag = self.getEmployeeExist(this_man_id)
            if exist_flag:
                this_time_num = self.getAttendanceWorkTime(this_man_id, this_code, this_work_card, this_first_card,
                                                           this_last_card)
                # 以 人的工号为 Keys
                if this_man_id not in all_data_dic.keys():
                    value_list = [this_time_num]
                    all_data_dic[this_man_id] = value_list
                else:
                    this_value_list = all_data_dic[this_man_id]
                    this_value_list.append(this_time_num)

        return all_data_dic

    @staticmethod
    def getListNum(list_data, val_data):
        """
        @note: 获取元素在列表中的下标
        """
        this_list_num = None
        val_data = datetime.strptime(val_data, "%H:%M:%S")
        for each_data in list_data:
            if val_data >= each_data:
                this_list_num = list_data.index(each_data)

        return this_list_num

    def getEmployeeExist(self, man_number):
        """
        @note: 判断 该员工是否是 师级 and 常設
        """
        emp_where_sql = "e_id='" + man_number + "' and " + \
                        "e_grade like '%" + u"師" + "%'" + \
                        " and e_category ='" + u"常設" + "'"
        employee_tup = self.dml_obj.selectData("e_id", GeneralParameters.employee_table, emp_where_sql)
        if employee_tup:
            exist_flag = True
        else:
            exist_flag = False

        return exist_flag

    def getEmployeeExist_Staff_Level(self, man_number):
        """
        @note: 包含员级
        """
        emp_where_sql = "e_id='" + man_number + "' and " + \
                        " e_category ='" + u"常設" + "'"
        employee_tup = self.dml_obj.selectData("e_id", GeneralParameters.employee_table, emp_where_sql)
        if employee_tup:
            exist_flag = True
        else:
            exist_flag = False

        return exist_flag

    def getXlsPath(self, data_xls):
        """
        @note: 获取 excle 文件的 路径
        """
        print "getXlsPath data_xls[0]:", data_xls[0]
        this_path = data_xls[0]
        dir_list = os.listdir(this_path)
        new_dir = self.getNewDir(dir_list)
        print "new_dir:", new_dir
        # new_dir = '2018-03-12-23-00-11'
        date_dir_path = os.path.join(this_path, new_dir)
        print "date_dir_path:", date_dir_path
        file_name = os.listdir(date_dir_path)[0]

        xls_path = os.path.join(date_dir_path, file_name)
        print "xls_path:", xls_path
        if xls_path:
            return xls_path
        else:
            return ""

    @staticmethod
    def getXlsData(xls_path):
        """
        @note: 引用 Sara 写的 API读取带有'<table><td>...'的excle文件，得到二维数组
        """
        _obj = ExportTableData(xls_path)
        all_list = _obj.table_data
        return all_list

    @staticmethod
    def getXlsDate(data):
        """
        @note: 获取该 excle 的年月
        """
        this_xls_mouth = data[0].split("/")[0]
        this_xls_mouth = int(this_xls_mouth)
        this_year = time.localtime().tm_year
        if this_xls_mouth == 12:
            this_xls_year = this_year - 1
        else:
            this_xls_year = this_year
        this_xls_date = str(this_xls_year) + "-" + str(this_xls_mouth) + "-" + "01"
        this_xls_date = datetime.strptime(this_xls_date, "%Y-%m-%d")
        return this_xls_date

    @staticmethod
    def getYearMouth():
        """
        @note: 获取 今年的年月和去年的年月 int
        """
        this_year = time.localtime().tm_year
        this_mouth = time.localtime().tm_mon
        if this_mouth == 1:
            prior_year = this_year - 1
            prior_mouth = 12
        else:
            prior_year = this_year
            prior_mouth = this_mouth - 1
        return this_year, this_mouth, prior_year, prior_mouth

    @staticmethod
    def getNewDate(year_val, mouth_val, str_val):
        """
        @note: 把日期格式的string 转化成 datetime
        """
        this_now_date = str(year_val) + "-" + str(mouth_val) + "-" + str_val
        this_now_date = datetime.strptime(this_now_date, "%Y-%m-%d")
        return this_now_date

    @staticmethod
    def getNewDir(dir_list):
        """
        @note: 获取该目录下最新的文件夹
        """
        n = len(dir_list)
        new_dir = dir_list[0]
        for r in range(1, n):
            if datetime.strptime(dir_list[r], "%Y-%m-%d-%H-%M-%S") > datetime.strptime(new_dir, "%Y-%m-%d-%H-%M-%S"):
                new_dir = dir_list[r]

        return new_dir

    def getFK(self, fk_table_id, fk_name, this_fk_val, fk_table):
        """
        @note: get fk's id,根据条件获取 db 中的信息
        """
        if not this_fk_val:
            return None
        fk_val_list = self.dml_obj.selectData(fk_table_id, fk_table, fk_name + " = '" + this_fk_val + "'")
        if not fk_val_list:
            fk_val = None
        else:
            fk_val = fk_val_list[0][0]
        return fk_val

    def getList(self, db_code, table_name, this_keyword_name=None, this_keyword_val=None):
        """
        @note: 解析从数据库获得元组，分解成列表
        """
        if this_keyword_name:
            tup_list = self.dml_obj.selectData(db_code, table_name, this_keyword_name + " = '" + this_keyword_val + "'")
        else:
            tup_list = self.dml_obj.selectData(db_code, table_name)
        db_code_list = [code_tup[0] for code_tup in tup_list]

        return db_code_list

    def getListLen(self, DB_code, table_name, where_sql):
        """
        @note: 解析从数据库获得元组，分解成列表
        """
        tup_list = self.dml_obj.selectData(DB_code, table_name, where_sql)
        db_code_list = [code_tup[0] for code_tup in tup_list]
        this_len = len(db_code_list)

        return this_len

    def insertAttendance(self):
        """
        @note:  月5號生成   員工考勤信息:
        """
        self.file_object.write("\n ---------------------Attendance 员工考勤信息----------------------- \n")
        self.writeTxt("insert Attendance员工考勤信息", "Beginning")
        # 获得 今年今月  
        this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()
        # this_year, this_mouth, prior_year, prior_mouth = 2019, 8, 2019, 7

        # 判断 数据库中 是否存在该月数据 避免重复插入
        db_need_date = self.getNewDate(prior_year, prior_mouth, "05")
        if self.dml_obj.selectData("a_id", GeneralParameters.attendance_table,
                                   "a_datetime = to_date('" + str(db_need_date) + "','yyyy-mm-dd hh24:mi:ss')"):
            print " eattendance 中 已存在该日期 资料"
            logging.info("End insertAttendance: EAttendance is already exist!!")
            self.writeTxt("insert Attendance员工考勤信息", "资料已存在，不需写入数据库")
            return

        # 从数据库中获取 前一个月的 刷卡 数据
        prior_now_date = self.getNewDate(prior_year, prior_mouth, "01")
        now_date = self.getNewDate(this_year, this_mouth, "01")
        crd_where_sql = "c_firstcrad is not null" + \
                        " and c_lastcard is not null " + \
                        " and c_datetype !='" + u"節假日" + "'" + \
                        " and c_datetime >= to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss')" + \
                        " and c_datetime < to_date('" + str(now_date) + "','yyyy-mm-dd hh24:mi:ss') order by c_datetime"
        all_crd_data_dic = self.getAllCrdData(crd_where_sql, GeneralParameters.crd_table)
        # all_crd_data_dic = self.getAllCrdData(crd_where_sql, GeneralParameters.lmf_crd_table)

        new_crd_dic = self.arrangeCrdData(all_crd_data_dic)

        # 写进 db 时， 需要的 数组格式 [[],[],[],....]
        insert_crd_data = []
        for each_man, each_list in new_crd_dic.items():
            man_tup = self.dml_obj.selectData("e_cname,e_leader,e_functionteam", GeneralParameters.employee_table,
                                              "e_id = '%s'" % each_man)
            man_cname = man_tup[0][0]
            man_leader = man_tup[0][1]
            man_team = man_tup[0][2]
            man_list = [db_need_date, each_man, man_cname, man_leader, man_team]
            man_list.extend(each_list[:16])
            man_list.append(each_list[17])
            man_list[7] = round(self.time_to_float(man_list[7]), 3)
            man_list[11] = round(self.time_to_float(man_list[11]), 3)
            man_list[14] = round(self.time_to_float(man_list[14]), 3)
            man_list[21] = round(self.time_to_float(man_list[21]), 3)
            insert_crd_data.append(man_list)

        if insert_crd_data:
            self.insertExcept(insert_crd_data, GeneralParameters.attendance_order_string,
                              GeneralParameters.attendance_table, "insert Attendance员工考勤信息")
            logging.info("End insertAttendance!!")
        else:
            self.writeTxt("insert Attendance员工考勤信息", "没有计算出数据")
            logging.info("End insertAttendance: insert_crd_data is null")
        self.writeTxt("insert Attendance员工考勤信息", "Finished")

    def getAllCrdData(self, crd_where_sql, crd_table_name):
        """
        @note:  从数据库中获取 前一个月的 刷卡 数据
        """
        unique_tup = self.dml_obj.selectData(
            "eemployee_id,c_datetime,c_workcrad,c_firstcrad,c_closedcard,c_lastcard,c_code,c_type,c_datetype",
            crd_table_name, crd_where_sql)

        all_crd_data_dic = {}

        for each_tup in unique_tup:
            this_man_id = str(each_tup[0])
            this_datetime = each_tup[1]
            this_work_card = each_tup[2]
            this_first_card = each_tup[3]
            this_closed_card = each_tup[4]
            this_last_card = each_tup[5]
            this_code = each_tup[6]
            this_type = each_tup[7]
            this_date_type = each_tup[8]
            each_list = [this_datetime, this_work_card, this_first_card, this_closed_card, this_last_card, this_code,
                         this_type, this_date_type]

            # if this_man_id == 'F1236398':
            # 只要常设师级
            exist_flag = self.getEmployeeExist(this_man_id)
            if exist_flag:
                if this_man_id not in all_crd_data_dic.keys():
                    all_crd_data_dic[this_man_id] = [each_list]
                else:
                    this_value_list = all_crd_data_dic[this_man_id]
                    this_value_list.append(each_list)

        return all_crd_data_dic

    def getAllCrdData_Free(self, crd_where_sql, crd_table_name):
        """
        @note:  从数据库中获取 前一个月的 刷卡 数据
        """
        unique_tup = self.dml_obj.selectData(
            "eemployee_id,c_datetime,c_workcrad,c_firstcrad,c_closedcard,c_lastcard,c_code,c_type,c_datetype",
            crd_table_name, crd_where_sql)

        all_crd_data_dic = {}

        for each_tup in unique_tup:
            this_man_id = str(each_tup[0])
            this_datetime = each_tup[1]
            this_work_card = each_tup[2]
            this_first_card = each_tup[3]
            this_closed_card = each_tup[4]
            this_last_card = each_tup[5]
            this_code = each_tup[6]
            this_type = each_tup[7]
            this_date_type = each_tup[8]
            each_list = [this_datetime, this_work_card, this_first_card, this_closed_card, this_last_card, this_code,
                         this_type, this_date_type]

            # if this_man_id == 'F1236398':
            # 只要常设师级
            exist_flag = self.getEmployeeExist_Staff_Level(this_man_id)
            if exist_flag:
                if this_man_id not in all_crd_data_dic.keys():
                    all_crd_data_dic[this_man_id] = [each_list]
                else:
                    this_value_list = all_crd_data_dic[this_man_id]
                    this_value_list.append(each_list)

        return all_crd_data_dic

    def getOverHoursData(self, man_id, date_time):
        """
        @note: 在 EOverhours DB 中，查看有效加班時數
        """
        all_date_list = ['h_01', 'h_02', 'h_03', 'h_04', 'h_05', 'h_06', 'h_07', 'h_08', 'h_09', 'h_10',
                         'h_11', 'h_12', 'h_13', 'h_14', 'h_15', 'h_16', 'h_17', 'h_18', 'h_19', 'h_20',
                         'h_21', 'h_22', 'h_23', 'h_24', 'h_25', 'h_26', 'h_27', 'h_28', 'h_29', 'h_30', 'h_31']
        date_num = date_time.day - 1
        this_db_need_val = all_date_list[date_num]
        this_db_need_time_val = str(date_time.year) + '-' + str(date_time.month) + '-01 00:00:00'

        this_sql_where = "eemployee_id = '" + man_id + "' and " + \
                         "h_yearmouth = to_date('%s', 'yyyy-mm-dd hh24:mi:ss')" % (this_db_need_time_val)
        crd_tup = self.dml_obj.selectData("%s" % this_db_need_val, GeneralParameters.over_hours_table, this_sql_where)
        if crd_tup:
            return crd_tup[0][0]
        else:
            return 0

    def arrangeCrdData(self, all_crd_data_dic):
        """
        @note: 整理考勤数据
        """
        crd_dic = {}
        for each_man, crd_data_list in all_crd_data_dic.items():

            work_hours_list, total_work_hours_time, duty_hours_list, total_duty_hours_time, over_hours_list, total_over_hours_time, each_one_night_val, last_card_list, total_last_card_time, offDutyNum = self.getCalculateCrdData(
                each_man, crd_data_list)

            # 计算
            # 總工作時長    工作天數    平均工作時長    最大工作時長
            total_hours, total_days, avg_hours, max_hours = self.arrangeAttendanceData(work_hours_list,
                                                                                       total_work_hours_time)

            # 總義務時長    平均義務時長    最大義務時長    義務工作天數
            total_duty_hours, total_duty_days, avg_duty_hours, max_duty_hours = self.arrangeAttendanceData(
                duty_hours_list, total_duty_hours_time)

            # 總超時工作    平均超時時長    最大超時時長
            total_over_hours, total_over_days, avg_over_hours, max_over_hours = self.arrangeAttendanceData(
                over_hours_list, total_over_hours_time)

            # 平均白班下班時間    最晚白班下班時間 compare_time_val
            if last_card_list:
                last_card_list.sort()
                avg_hours_time = total_last_card_time / len(last_card_list)
                avg_hours_time = datetime.strptime('2018-01-01 00:00:00', '%Y-%m-%d %H:%M:%S') + avg_hours_time
                avg_hours_val = avg_hours_time.replace(microsecond=0)
                avg_last_card_str = str(avg_hours_val)
                avg_last_card_val = avg_last_card_str.split(' ')[-1]
                max_last_card_str = str(last_card_list[-1])
                max_last_card_val = max_last_card_str.split(' ')[-1]

                # 计算  超[20:05, 22:00] 的天次 以及 大于[20:05]的时数和
                over_eight_num, total_over_eight_time, over_ten_num, = self.getOverTime(last_card_list)

            crd_dic[each_man] = [total_hours, avg_hours, max_hours, total_days,
                                 total_over_hours, avg_over_hours, max_over_hours,
                                 total_duty_hours, avg_duty_hours, max_duty_hours, total_duty_days,
                                 avg_last_card_val, max_last_card_val, each_one_night_val, offDutyNum[0], offDutyNum[1],
                                 over_eight_num, total_over_eight_time, over_ten_num]

        return crd_dic

    def getCalculateCrdData(self, each_man, crd_data_list):
        """
        @note: each_crd_data: [this_datetime, this_work_card, this_first_card, this_closed_card, this_last_card, this_code, this_type, this_date_type]
        @note: 获取  work_hours_list,total_work_hours_time,duty_hours_list,total_duty_hours_time,over_hours_list,total_over_hours_time,each_one_night_val,last_card_list,total_last_card_time, offDutyNum
        """
        work_hours_list = []
        total_work_hours_time = timedelta(hours=0)
        duty_hours_list = []
        total_duty_hours_time = timedelta(hours=0)
        over_hours_list = []
        total_over_hours_time = timedelta(hours=0)
        each_one_night_val = 0
        last_card_list = []
        total_last_card_time = timedelta(hours=0)
        # [準點下班天數, 非準點下班天數]
        offDutyNum = [0, 0]

        for each_crd_data in crd_data_list:
            # 获得该天 休息的时间
            lunch_rest_time, dinner_rest_time = self.getAttendanceRestTime(each_man, each_crd_data[5])

            # 工作开始时间: 上班打卡时间  标准下班时间  规定上班打卡时间
            day_time_val, standard_work_time_date, work_first_up = self.getWorkTime(each_crd_data, lunch_rest_time,
                                                                                    dinner_rest_time)

            # 01:实际每天工作时长 ,type -- timedelta   work_hours_date--下班时间 = 上班时间 + 工作时长 + 休息时间
            work_hours_val = self.getAttendanceWorkTime(each_man, each_crd_data[5], each_crd_data[1], each_crd_data[2],
                                                        each_crd_data[4])
            work_hours_date = day_time_val + work_hours_val + lunch_rest_time + dinner_rest_time
            work_hours_list.append(work_hours_val)
            total_work_hours_time = total_work_hours_time + work_hours_val

            # 02:獲取該員工 是否存在 有效加班時數 int
            valid_hours_val = self.getOverHoursData(each_man, each_crd_data[0])

            # 03:义务工作时长 -- timedelta    # 工作日    節假日    周休日
            interval_work_standard = work_hours_date - standard_work_time_date
            if each_crd_data[7] == '工作日' and interval_work_standard < timedelta(hours=0):
                duty_hours_val = timedelta(hours=0)
                overtime_hours_val = timedelta(hours=0)
            elif each_crd_data[7] == '周休日' and work_hours_val >= timedelta(hours=valid_hours_val):
                if valid_hours_val:
                    # 标准下班时间:  有提报加班时数
                    standard_closed_work = work_first_up + timedelta(
                        hours=valid_hours_val) + lunch_rest_time + dinner_rest_time
                    if work_hours_date > standard_closed_work:
                        duty_hours_val = work_hours_val - timedelta(hours=valid_hours_val)
                    else:
                        duty_hours_val = timedelta(hours=0)
                else:
                    duty_hours_val = work_hours_val
                overtime_hours_val = work_hours_val
            elif each_crd_data[7] == '周休日' and work_hours_val < timedelta(hours=valid_hours_val):
                # 标准下班时间
                standard_closed_work = work_first_up + timedelta(
                    hours=valid_hours_val) + lunch_rest_time + dinner_rest_time
                if work_hours_date > standard_closed_work:
                    duty_hours_val = work_hours_date - standard_closed_work
                else:
                    duty_hours_val = timedelta(hours=0)
                overtime_hours_val = work_hours_val
            elif each_crd_data[7] == '工作日' and interval_work_standard < timedelta(hours=valid_hours_val):
                duty_hours_val = timedelta(hours=0)
                overtime_hours_val = work_hours_date - standard_work_time_date
            elif each_crd_data[7] == '工作日' and interval_work_standard >= timedelta(hours=valid_hours_val):
                duty_hours_val = work_hours_date - standard_work_time_date - timedelta(hours=valid_hours_val)
                overtime_hours_val = work_hours_date - standard_work_time_date

            if duty_hours_val > timedelta(hours=0):
                duty_hours_list.append(duty_hours_val)
                total_duty_hours_time = total_duty_hours_time + duty_hours_val

            # 04:超时工作时长:去掉第二段下班时间,超时工作时长  -- timedelta
            over_hours_list.append(overtime_hours_val)
            total_over_hours_time = total_over_hours_time + overtime_hours_val

            # 05: 晚班次数
            if each_crd_data[6] == '晚班':
                each_one_night_val = each_one_night_val + 1

            # 06: 白班下班時間 以及 [准點下班天數、非准點下班天數]
            if each_crd_data[6] == '白班':
                last_card_list.append(work_hours_date)
                time_list = ['18:05:00', '19:30:00', '20:00:00', '20:30:00', '21:00:00', '21:30:00', '22:00:00',
                             '22:30:00', '23:00:00']
                getIndexNum = self.analysisTime(each_crd_data[4], time_list)
                # 周休日和節假日 扣除有效加班時數
                last_card_hours_time = work_hours_date - datetime.strptime('2018-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
                total_last_card_time = total_last_card_time + last_card_hours_time
            man_type_tup = self.dml_obj.selectData("e_difference", GeneralParameters.employee_table,
                                                       "e_id = '%s'" % each_man)

            work_list = self.dml_obj.selectData("C_BEGINOVER,c_type",  GeneralParameters.classes_table, "c_code='{}'".format(each_crd_data[5]))
            today_year = each_crd_data[0].year
            today_month = each_crd_data[0].month
            today_day = each_crd_data[0].day
            offworktime = str(today_year) + '-' + str(today_month) + '-' + str(today_day) + " " + work_list[0][0] +":00"
            offhour = int(work_list[0][0].split(':')[0])
            if work_list[0][1] != '晚班':
                offworkdate = datetime.strptime(offworktime, "%Y-%m-%d %H:%M:%S")
            else:
                if offhour < 19:
                    offworkdate = datetime.strptime(offworktime, "%Y-%m-%d %H:%M:%S") + timedelta(days=1)
                else:
                    offworkdate = datetime.strptime(offworktime, "%Y-%m-%d %H:%M:%S")
            if man_type_tup[0][0] != '中干' and man_type_tup[0][0] != '中幹':
                # 台干周六也是工作日
                if each_crd_data[4] - datetime.strptime(str(today_year) + '-' + str(today_month) + '-' + str(today_day) + " " + "17:30:00", "%Y-%m-%d %H:%M:%S") >= timedelta(minutes=35):
                    offDutyNum[1] = offDutyNum[1] + 1
                else:
                    offDutyNum[0] = offDutyNum[0] + 1
            else:
                if each_crd_data[7] == '工作日':
                    if each_crd_data[4] - offworkdate >= timedelta(minutes=35):
                        offDutyNum[1] = offDutyNum[1] + 1
                    else:

                        offDutyNum[0] = offDutyNum[0] + 1
                else:
                    if each_crd_data[4]:
                        offDutyNum[1] = offDutyNum[1] + 1

        return work_hours_list, total_work_hours_time, duty_hours_list, total_duty_hours_time, over_hours_list, total_over_hours_time, each_one_night_val, last_card_list, total_last_card_time, offDutyNum

    def getWorkTime(self, crd_data, lunch_rest_time, dinner_rest_time):
        """
        @note: 获取 员工的上班打卡时间，标准工作时长，标准上班打卡时间
        @note: c_datetime,c_workcrad,c_firstcrad,c_closedcard,c_lastcard,c_code,c_type,c_datetype
        """
        #         print "lunch_rest_time:", lunch_rest_time
        #         print "dinner_rest_time:", dinner_rest_time
        day_time_val = datetime.strptime('2018-01-01 ' + crd_data[1] + ':00', '%Y-%m-%d %H:%M:%S')

        # 获取改班别的 上班打卡时间
        work_time_list = self.getAttendanceClassesTime(crd_data[5])
        work_first_up = work_time_list[0]
        work_first_down = work_time_list[1]
        work_second_up = work_time_list[2]
        work_second_down = work_time_list[3]

        standard_work_val = work_second_down - work_first_up
        standard_work_time_date = day_time_val + standard_work_val + dinner_rest_time
        first_card_str = '2018-01-01 ' + str(crd_data[2]).split(' ')[-1]
        first_card_val = datetime.strptime(first_card_str, '%Y-%m-%d %H:%M:%S')
        if first_card_val < work_first_up:
            day_time_val = work_first_up
        elif work_first_up < first_card_val < work_first_down:
            day_time_val = first_card_val
        elif work_first_down <= first_card_val <= work_second_up:
            day_time_val = work_second_up
        elif work_second_up < first_card_val <= work_second_down:
            day_time_val = first_card_val
        else:
            day_time_val = first_card_val

        return day_time_val, standard_work_time_date, work_first_up

    @staticmethod
    def arrangeAttendanceData(_list, total_time):
        """
        @note: 计算 总的时间   总的长度  平均时间   最大时长
        """
        if len(_list) >= 1:
            _list.sort()
            total_hours_date = total_time.total_seconds()
            total_hours_date = total_hours_date / (60 * 60)
            db_total_hours = decimal.Decimal("%.2f" % float(total_hours_date))
            db_total_days = len(_list)
            db_avg_hours = total_hours_date / db_total_days
            db_avg_hours = decimal.Decimal("%.2f" % float(db_avg_hours))
            db_max_hours = str(_list[-1])
        else:
            db_total_hours = 0
            db_total_days = 0
            db_avg_hours = 0
            db_max_hours = ''

        return db_total_hours, db_total_days, db_avg_hours, db_max_hours

    def getAttendanceWorkTime(self, each_man, code_val, work_card_val, first_time_val, last_time_val):
        """
        @note: 判断  工作多长时间
        """
        # 获得该天 休息的时间
        lunch_rest_time, dinner_rest_time = self.getAttendanceRestTime(each_man, code_val)

        # 获取员工上班卡时间格式
        time_val_str = str(first_time_val)
        work_card_val = time_val_str.split(" ")[0] + " " + work_card_val + ":00"
        work_card_val_time = datetime.strptime(work_card_val, "%Y-%m-%d %H:%M:%S")

        # 计算该天 工作时数
        if first_time_val > work_card_val_time:
            this_time_num = last_time_val - first_time_val
        else:
            this_time_num = last_time_val - work_card_val_time

        if this_time_num < timedelta(hours=0):
            last_time_val = last_time_val + timedelta(hours=24)
            if first_time_val > work_card_val_time:
                this_time_num = last_time_val - first_time_val
            else:
                this_time_num = last_time_val - work_card_val_time
        # 再减去休息的时间
        this_time_num = this_time_num - lunch_rest_time - dinner_rest_time
        return this_time_num

    def getAttendanceRestTime(self, each_man, classes_code):
        """
        @note: 根据 员工的工号以及班别，获取该班别的 ‘中午吃饭时间和晚上吃饭时间’
        @note: 区别 中干 与  台干: 台干 暂时做特殊处理
        """
        # 中午休息时间  和  下班与加班之间休息时间
        man_type_tup = self.dml_obj.selectData("e_difference", GeneralParameters.employee_table,
                                               "e_id = '%s'" % each_man)
        if man_type_tup[0][0] != '中干' or man_type_tup[0][0] != '中幹':
            lunch_rest_time = datetime.strptime('2018-01-01 13:30:00', "%Y-%m-%d %H:%M:%S") - datetime.strptime(
                '2018-01-01 12:00:00', "%Y-%m-%d %H:%M:%S")
            dinner_rest_time = datetime.strptime('2018-01-01 17:30:00', "%Y-%m-%d %H:%M:%S") - datetime.strptime(
                '2018-01-01 17:30:00', "%Y-%m-%d %H:%M:%S")
        else:
            work_time_list = self.getAttendanceClassesTime(classes_code)
            lunch_rest_time = work_time_list[0] - work_time_list[1]
            dinner_rest_time = work_time_list[4] - work_time_list[3]

        return lunch_rest_time, dinner_rest_time

    def getAttendanceClassesTime(self, classes_code):
        """
        @note: 根据班别 获取 改班别的 打卡时间
        @note: 第一段上班打卡时间,第一段下班打卡时间,第二段上班打卡时间,第二段下班打卡时间, 加班开始时间
        @note: work_first_up, work_first_down, work_second_up, work_second_down, work_begin_over
        """
        classes_tup = self.dml_obj.selectData("c_firstup,c_firstdown,c_secondeup,c_secondedown,c_beginover,c_type",
                                              GeneralParameters.classes_table, "c_code='%s'" % classes_code)
        if classes_tup:
            this_classes_massage = classes_tup[0]
            this_c_first_up = '2018-01-01 ' + this_classes_massage[0] + ":00"
            this_c_first_down = '2018-01-01 ' + this_classes_massage[1] + ":00"
            this_c_second_up = '2018-01-01 ' + this_classes_massage[2] + ":00"
            this_c_second_down = '2018-01-01 ' + this_classes_massage[3] + ":00"
            this_c_begin_over = '2018-01-01 ' + this_classes_massage[4] + ":00"

            # 判断 是否隔天
            if this_c_first_down < this_c_first_up:
                this_c_second_up = '2018-01-02 ' + this_classes_massage[2] + ":00"
                this_c_second_down = '2018-01-02 ' + this_classes_massage[3] + ":00"
                this_c_begin_over = '2018-01-02 ' + this_classes_massage[4] + ":00"
            elif this_c_first_down > this_c_second_up:
                this_c_second_up = '2018-01-02 ' + this_classes_massage[2] + ":00"
                this_c_second_down = '2018-01-02 ' + this_classes_massage[3] + ":00"
                this_c_begin_over = '2018-01-02 ' + this_classes_massage[4] + ":00"
            elif this_c_first_down > this_c_second_down:
                this_c_second_down = '2018-01-02 ' + this_classes_massage[3] + ":00"
                this_c_begin_over = '2018-01-02 ' + this_classes_massage[4] + ":00"
            elif this_c_first_down > this_c_begin_over:
                this_c_begin_over = '2018-01-02 ' + this_classes_massage[4] + ":00"

            work_first_up = datetime.strptime(this_c_first_up, "%Y-%m-%d %H:%M:%S")
            work_first_down = datetime.strptime(this_c_first_down, "%Y-%m-%d %H:%M:%S")
            work_second_up = datetime.strptime(this_c_second_up, "%Y-%m-%d %H:%M:%S")
            work_second_down = datetime.strptime(this_c_second_down, "%Y-%m-%d %H:%M:%S")
            work_begin_over = datetime.strptime(this_c_begin_over, "%Y-%m-%d %H:%M:%S")
            work_time_list = [work_first_up, work_first_down, work_second_up, work_second_down, work_begin_over]
        if work_time_list:
            return work_time_list
        else:
            work_time_list = [timedelta(hours=0), timedelta(hours=0),
                              timedelta(hours=0), timedelta(hours=0), timedelta(hours=0)]
            return work_time_list

    def getOverTime(self, work_time_list):
        """
        @note: 计算  超[20:05, 22:00] 的天次 以及 大于[20:05]的时数和
        """
        eight_time = datetime.strptime('2018-01-01 20:05:00', '%Y-%m-%d %H:%M:%S')
        ten_time = datetime.strptime('2018-01-01 22:00:00', '%Y-%m-%d %H:%M:%S')
        over_eight_num = 0
        total_over_eight_time = timedelta(hours=0)

        over_ten_num = 0

        for each_time in work_time_list:
            if each_time >= ten_time:
                over_ten_num += 1
            if each_time >= eight_time:
                over_eight_num += 1
                total_over_eight_time = each_time - eight_time + total_over_eight_time
        return over_eight_num, str(total_over_eight_time), over_ten_num,

    def insertLateMealFee(self):
        """
        @note: "eemployee_id,c_datetime,c_workcrad,c_firstcrad,c_closedcard,c_lastcard,c_code,c_type,c_datetype"
        @note: 计算每周的 误餐费
        """
        self.file_object.write("\n ---------------------insertLateMealFee 周晚点下班统计----------------------- \n")
        self.writeTxt("insert insertLateMealFee周晚点下班统计", "Beginning")
        # 有当天日期 获取  该年周数，以及星期一 和星期天的 日期
        dayfrom = datetime.now() - timedelta(days=datetime.now().isoweekday()) - timedelta(days=6)
        now_date_time = datetime(dayfrom.year, dayfrom.month, dayfrom.day, 0, 0, 0)
        # 测试
        # now_str = str(2019) + str(10) + str('%d' %1)
        # now_date_time = datetime.strptime(now_str, '%Y%m%d')

        this_weekday = now_date_time.weekday()
        week_number = now_date_time.isocalendar()
        week_number_value = int(str(week_number[0]) + str(week_number[1]))

        # 获取 周一的日期 周日的日期
        monday_time = now_date_time + timedelta(days=-this_weekday)
        sunday_time = monday_time + timedelta(days=6)
        interval_str = str(monday_time).split(" ")[0] + "~" + str(sunday_time).split(" ")[0]
        interval_str = interval_str.replace("-", ".")

        if self.dml_obj.selectData("l_id", GeneralParameters.late_meal_fee_table,
                                   "l_datetime = to_date('" + str(monday_time) + "','yyyy-mm-dd hh24:mi:ss')"):
            print " 已存在 该日期资料"
            print "----- Finished insert LateMealFee!!"
            logging.info("End insertDBData: LateMealFee is already exist!!")
            self.writeTxt("insert LateMealFee", "资料已存在，不需写入数据库")
            return ""

        crd_where_sql = "c_firstcrad is not null" + \
                        " and c_lastcard is not null " + \
                        " and c_datetype !='" + u"節假日" + "'" + \
                        " and c_datetime >= to_date('" + str(monday_time) + "','yyyy-mm-dd hh24:mi:ss')" + \
                        " and c_datetime <= to_date('" + str(
            sunday_time) + "','yyyy-mm-dd hh24:mi:ss') order by c_datetime"
        all_crd_data_dic = self.getAllCrdData_Free(crd_where_sql, GeneralParameters.lmf_crd_table)
        # all_crd_data_dic = self.getAllCrdData(crd_where_sql, GeneralParameters.crd_table)

        insert_lmf_data = []
        dic_personal_data = {}
        for each_man, crd_data_list in all_crd_data_dic.items():
            # 计算当周 晚上20点以后下班的 次数
            over_8_num = 0  # 10.5小时
            over_9_num = 0  # 11小时
            over_10_num = 0 # 12小时
            over_11_num = 0 # 13小时

            time_list = ['9:00:00', '9:30:00', '10:00:00', '10:30:00', '11:00:00', '11:30:00', '12:00:00',
                         '12:30:00', '13:30:00']

            for each_crd_data in crd_data_list:
                # print each_crd_data
                # 指定格式
                row = (each_man, each_crd_data[0], each_crd_data[4], each_crd_data[5], each_crd_data[6], each_crd_data[2], each_crd_data[7])
                # 测试
                # row = (each_man, each_crd_data[0], each_crd_data[4] + timedelta(hours=4.5), each_crd_data[5], each_crd_data[6], each_crd_data[2], each_crd_data[7])

                # 个人
                if row[0] not in dic_personal_data.keys():
                    dic_personal_data[each_man] = [each_man, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                # 获取是否加班 和 工作小时数
                t_index, overtime_bool = self.ga_analysisTime(row, time_list)

                # 异常数据过滤
                if t_index == 999:
                    continue

                # 工作时长没有超过9小时,略过
                if t_index == 100:
                    continue
                # 工作时超过9小时
                # 个人
                for j in range(1, t_index + 2):
                    dic_personal_data[each_man][j] += 1

                continue
            # 超时时长赋值
            over_8_num = dic_personal_data[each_man][4]
            over_9_num = dic_personal_data[each_man][6]
            over_10_num = dic_personal_data[each_man][8]
            over_11_num = dic_personal_data[each_man][9]

            man_tup = self.dml_obj.selectData("e_cname,e_leader", GeneralParameters.employee_table,
                                              "e_id = '%s'" % each_man)
            man_cname = man_tup[0][0]
            man_leader = man_tup[0][1]
            insert_lmf_data.append(
                [monday_time, each_man, man_cname, man_leader, interval_str, week_number_value, over_10_num, over_8_num,
                 over_9_num, over_11_num])

        if insert_lmf_data:
            self.insertExcept(insert_lmf_data, GeneralParameters.late_meal_fee_order_string,
                              GeneralParameters.late_meal_fee_table, "insert LMF insertLateMealFee")
            logging.info("End insertLateMealFee!!")
        else:
            self.writeTxt("insert insertLateMealFee", "没有数据")
        self.writeTxt("insert LMF insertLateMealFee", "Finished")
        print "Finished"

    def insertLMFAttendance(self):
        """
        @note: 
        """
        self.file_object.write("\n ---------------------LMFAttendance 员工考勤信息----------------------- \n")
        self.writeTxt("insert LMFAttendance员工考勤信息", "Beginning")
        # 获得 今年今月  
        now_year = time.localtime().tm_year
        now_month = time.localtime().tm_mon
        now_day = time.localtime().tm_mday
        # now_month = 4
        # now_day = 1
        if now_day > 1:
            prior_now_date = self.getNewDate(now_year, now_month, "01")
            now_date = self.getNewDate(now_year, now_month, str(now_day))
            db_need_date = self.getNewDate(now_year, now_month, "05")
            total_month_days = calendar.monthrange(now_year, now_month)[1]
            interval_str = str(now_year) + "." + str(now_month) + ".01~" + str(now_year) + "." + str(
                now_month) + "." + str(now_day - 1)
        elif now_day == 1 and now_month != 1:
            prior_now_date = self.getNewDate(now_year, now_month - 1, "01")
            now_date = self.getNewDate(now_year, now_month, "01")
            db_need_date = self.getNewDate(now_year, now_month - 1, "05")
            total_month_days = calendar.monthrange(now_year, now_month - 1)[1]
            # interval_str = str(now_year) + "." + str(now_month - 1) + ".01~" + str(now_year) + "." + str(
            #     now_month) + "." + str(now_day)
            interval_str = str(now_year) + "." + str(now_month - 1) + ".01~" + str(now_year) + "." + str(
                now_month - 1) + "." + str(total_month_days)
        elif now_day == 1 and now_month == 1:
            prior_now_date = self.getNewDate(now_year - 1, 12, "01")
            now_date = self.getNewDate(now_year, 1, "01")
            db_need_date = self.getNewDate(now_year - 1, 12, "05")
            total_month_days = calendar.monthrange(now_year - 1, 12)[1]
            interval_str = str(now_year - 1) + ".12.01~" + str(now_year) + ".12." + str(total_month_days)

        # print('db_need_date: ', db_need_date)
        # print('prior_now_date: ', prior_now_date)
        # print('now_date: ', now_date)
        crd_where_sql = "c_firstcrad is not null" + \
                        " and c_lastcard is not null " + \
                        " and c_datetype !='" + u"節假日" + "'" + \
                        " and c_datetime >= to_date('" + str(prior_now_date) + "','yyyy-mm-dd hh24:mi:ss')" + \
                        " and c_datetime < to_date('" + str(now_date) + "','yyyy-mm-dd hh24:mi:ss') order by c_datetime"
        all_crd_data_dic = self.getAllCrdData(crd_where_sql, GeneralParameters.lmf_crd_table)
        # print('all_crd_data_dic: ', all_crd_data_dic)
        new_crd_dic = self.arrangeCrdData(all_crd_data_dic)
        # print('new_crd_dic: ', new_crd_dic)
        # 写进 db 时， 需要的 数组格式 [[],[],[],....]
        insert_crd_data = []
        for each_man, each_list in new_crd_dic.items():
            try:
                man_tup = self.dml_obj.selectData("e_cname,e_leader,e_functionteam", GeneralParameters.employee_table,
                                                  "e_id = '%s'" % each_man)
                man_cname = man_tup[0][0]
                man_leader = man_tup[0][1]
                man_team = man_tup[0][2]
                man_list = [db_need_date, each_man, man_cname, man_leader, man_team, interval_str]
                man_list.extend(each_list)
                man_list[8] = round(self.time_to_float(man_list[8]), 3)
                man_list[12] = round(self.time_to_float(man_list[12]), 3)
                man_list[15] = round(self.time_to_float(man_list[15]), 3)
                man_list[23] = round(self.time_to_float(man_list[23]), 3)
                exist_sql = "a_datetime = to_date('" + str(db_need_date) + "','yyyy-mm-dd hh24:mi:ss') " + \
                            "and a_employee = '" + each_man + "'"
                if self.dml_obj.selectData("a_id", GeneralParameters.lmf_attendance_table, exist_sql):
                    sql_string = "update " + GeneralParameters.lmf_attendance_table + " set " + \
                                 "a_totalhours = " + str(each_list[0]) + ",a_avghours = " + str(each_list[1]) + \
                                 ",a_maxhours = " + str(round(self.time_to_float(each_list[2]), 3))+ ",a_totaldays = " + str(each_list[3]) + \
                                 ",a_totaloverhours = " + str(each_list[4]) + ",a_avgoverhours = " + str(each_list[5]) + \
                                 ",a_maxoverhours = " + str(round(self.time_to_float(each_list[6]), 3)) + ",a_totaldutyhours = " + str(each_list[7]) + \
                                 ",a_avgdutyhours = " + str(each_list[8]) + ",a_maxdutyhours = " + str(round(self.time_to_float(each_list[9]), 3)) + \
                                 ",a_dutydays = " + str(each_list[10]) + ",a_avglastcard = '" + each_list[11] + \
                                 "',a_maxlastcard = '" + each_list[12] + "',a_nightnum = " + str(each_list[13]) + \
                                 ",a_offduty = " + str(each_list[14]) + ",a_unoffduty = " + str(each_list[15]) + \
                                 ",a_eightlate = " + str(each_list[16]) + ",a_eighttotal = " + str(round(self.time_to_float(each_list[17]), 3)) + \
                                 ",a_tenlate = " + str(each_list[18]) + ",a_interval = '" + interval_str + \
                                 "',a_team='" + man_team + "' where " + "a_datetime = to_date('" + str(
                        db_need_date) + "','yyyy-mm-dd hh24:mi:ss') " + \
                                 "and a_employee = '" + each_man + "'"
                    self.dml_obj.updateData(sql_string)
                    # print('update lmf_attendance_table')
                else:
                    insert_crd_data.append(man_list)
            except Exception as e:
                self.writeTxt("insert LMF Attendance员工考勤信息", "更新数据发生错误")
                logging.info("End insertLMFAttendance: insert_crd_data is null")
        self.writeTxt("insert LMF Attendance员工考勤信息", "更新数据成功")
        # print('insert_crd_data:', insert_crd_data)
        if insert_crd_data:
            self.insertExcept(insert_crd_data, GeneralParameters.lmf_attendance_order_string,
                              GeneralParameters.lmf_attendance_table, "insert LMF Attendance员工考勤信息")
            logging.info("End insertLMFAttendance!!")
        self.writeTxt("insert LMF Attendance员工考勤信息", "Finished")

    def create_attendance_email_data(self):
        """处理 每月考勤状况发邮件所需的数据 每个部、每个课当年平均加班、当月加班"""
        now_year = time.localtime().tm_year
        now_month = time.localtime().tm_mon
        now_day = time.localtime().tm_mday
        # now_month = 7
        if now_month == 1:
            # 月份为1时 计算上一年，并且 小于5号时，计算上一年 11月的考勤数据(12月还没有数据)
            if now_day < 5:
                this_year_date = self.getNewDate(now_year - 1, 1, '01')
                this_month_date = self.getNewDate(now_year - 1, 11, "05")
                month_num = 11
            else:
                this_month_date = self.getNewDate(now_year - 1, 12, "05")
                month_num = 12
        else:
            this_year_date = self.getNewDate(now_year, 1, '01')
            if now_day < 5:
                this_month_date = self.getNewDate(now_year, now_month - 2, "05")
                month_num = now_month-2
            else:
                this_month_date = self.getNewDate(now_year, now_month - 1, "05")
                month_num = now_month-1

        # 从ESECTIONGREATERTHAN表里获取初始数据
        # 各个课 截止到当月的全年数据
        all_year_section_data = self.dml_obj.selectData("g_section, g_before6, g_than6",
                                                        GeneralParameters.section_greater_than_table,
                                                        "g_datetime >= to_date('" + str(
                                                            this_year_date) + "', 'yyyy-mm-dd hh24:mi:ss')")
        # 各个课 当月的数据
        current_month_section_data = self.dml_obj.selectData("g_section, g_before6, g_than6",
                                                             GeneralParameters.section_greater_than_table,
                                                             "g_datetime = to_date('" + str(
                                                                 this_month_date) + "', 'yyyy-mm-dd hh24:mi:ss')")
        # 各个部 截止到当月的全年数据
        all_year_department_data = self.dml_obj.selectData("g_leader, g_before6, g_than6",
                                                           GeneralParameters.greater_than_table,
                                                           "g_datetime >= to_date('" + str(
                                                               this_year_date) + "', 'yyyy-mm-dd hh24:mi:ss')")
        # 各个部 当月的数据
        current_month_department_data = self.dml_obj.selectData("g_leader, g_before6, g_than6",
                                                                GeneralParameters.greater_than_table,
                                                                "g_datetime = to_date('" + str(
                                                                    this_month_date) + "', 'yyyy-mm-dd hh24:mi:ss')")
        # print(len(all_year_section_data), all_year_section_data)
        # print(len(current_month_section_data), current_month_section_data)
        year_department_percentage = self.arrange_year_data(all_year_department_data, month_num)
        # year_department_percentage = self.get_percentage_data(sum_year_department_data)
        department_current_month_percentage = self.get_percentage_data(current_month_department_data)
        year_section_percentage = self.arrange_year_data(all_year_section_data, month_num)
        # year_section_percentage = self.get_percentage_data(sum_year_section_data)
        current_month_percentage = self.get_percentage_data(current_month_section_data)
        # print('year_section_percentage:', year_section_percentage)
        # print('current_month_percentage:', current_month_percentage)
        leader_team = self.get_leader_section()
        # 生成[['Don', 65.65, 64.68, ['EE Validation', 65.65, 64.68]], ['MG', 58.25, 61.1, ['RFHW', 58.25, 61.1]], ...]
        # 这种格式的数据
        table_data = []
        for k in leader_team.keys():
            _list = []
            _list.append(k)
            _list.append(year_department_percentage[k])
            _list.append(department_current_month_percentage[k])
            for v in leader_team[k]:
                _list.append([v, year_section_percentage[v], current_month_percentage[v]])

            table_data.append(_list)

        # print('table_data:', table_data)
        return table_data

    def arrange_year_data(self, year_data, month_num):
        """处理全年的数据: 每个月的数据加起来，保持本来的数据格式"""
        temp_arr = []
        for d in year_data:
            _list = []
            _list.append(d[0])
            _list.append(float('%.2f' % (float(d[2] * 100) / (d[1] + d[2]))))
            temp_arr.append(_list)

        temp_dict = {}
        for d in temp_arr:
            if d[0] not in temp_dict.keys():
                # temp_dict[d[0]] = d[1:]
                temp_dict[d[0]] = d[1]
            else:
                # temp_dict[d[0]] = (temp_dict[d[0]][0] + d[1], temp_dict[d[0]][1] + d[2])
                temp_dict[d[0]] = temp_dict[d[0]] + d[1]

        for k, v in temp_dict.items():
            temp_dict[k] = float('%.2f' % (v/month_num))
        # print('temp_dict:', temp_dict)
        # sum_this_year_data = []
        # for k in temp_dict.keys():
        #     temp_list = (k, temp_dict[k][0], temp_dict[k][1])
        #     sum_this_year_data.append(temp_list)

        # return sum_this_year_data
        return temp_dict

    def get_percentage_data(self, arr):
        # 把数字转成百分比 ['课', num, num] --> {'课':百分比}
        new_dict = {}
        for a in arr:
            new_dict[a[0]] = float('%.2f' % (float(a[2] * 100) / (a[1] + a[2])))
            # temp_list = (a[0], round(a[2]*100/(a[1]+a[2]), 2))
            # new_arr.append(temp_list)
        return new_dict

    def get_leader_section(self):
        """获取leader与对应的课级"""
        team_data = self.dml_obj.selectData('t_team, t_leader', GeneralParameters.team_table)
        # print(team_data)
        leader_team_dict = {}
        for i, t in enumerate(team_data):
            if t[1] not in leader_team_dict.keys():
                leader_team_dict[t[1]] = [t[0]]
            else:
                leader_team_dict[t[1]].append(t[0])
        # print('leader_team_dict', leader_team_dict)
        return leader_team_dict


    @staticmethod
    def time_to_float(time_str):
        try:
            hour_str, min_str, sec_str = time_str.split(':')
        except Exception as e:
            return 0.000
        try:
            hour_float = float(hour_str) + ((float(sec_str) + float(min_str)*60)/3600)
        except Exception as e:
            days_str = float((hour_str.split(', ')[0]).split(' ')[0])
            hour_str = hour_str.split(', ')[1]
            hour_float = (24*float(days_str)) + float(hour_str) + ((float(sec_str) + float(min_str)*60)/3600)
        return hour_float


    @staticmethod
    def setLog():
        """
        @note: set log file
        """
        dir_path = os.path.dirname(__file__)
        log_path = os.path.join(dir_path, 'EERF_Attendance.log')
        # 'asctime' 时间 ; 'levelname' level等级名 ; 'funcName' log所在函数名 
        # 'lineno' 行号 ; 'message' log内容
        logging.basicConfig(filename=log_path,
                            level=logging.INFO,
                            format='[%(asctime)s : %(levelname)s]--[%(funcName)s: %(lineno)d] : %(message)s')

    def createFolder(self):
        # title = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        folder_name = str(time.localtime().tm_year) + "-" + str(time.localtime().tm_mon) + "-" + str(
            time.localtime().tm_mday)
        self.folder_path = os.path.join(GeneralParameters.log_txt_path, folder_name)
        self.txt_path = os.path.join(self.folder_path, 'insertLog.txt')
        if not os.path.isdir(self.folder_path):
            os.makedirs(self.folder_path)
            self.file_object = open(self.txt_path, 'a')
        else:
            self.file_object = open(self.txt_path, 'a+')

    def closeOpen(self):
        self.file_object.close()

    def writeTxt(self, title, content):
        self.file_object.write(title + " (" + str(datetime.now()) + "): " + content + " !!!; \n")

    def insertExcept(self, data, order_string, table_name, function_name):
        try:
            self.dml_obj.insertData(data, order_string, table_name)
            self.writeTxt(function_name, "数据写入成功")
        except Exception as e:
            self.writeTxt(function_name, "数据写入失败")
            self.writeTxt("失败的原因是", str(e))


if __name__ == '__main__':
    instance = ArrangeDB()
