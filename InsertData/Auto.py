# -*- coding:utf-8 -*-
'''
@note: 
@note: get the data to insert
@author: F
'''
import os
import json, time
from xlwt import *
from datetime import datetime, timedelta

os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.AL32UTF8'
import csv
import chardet
import logging
import xlrd
import calendar

from generalParametes import GeneralParameters
from DMLData import oracle
from TableData import ExportTableData, OpenFile
import sys
from bs4 import BeautifulSoup
from collections import Counter

reload(sys)
sys.setdefaultencoding('utf8')


class ArrangeData():
    def __init__(self):
        """
        @note: split data for different table
        @note: insertDemand 和 insertRecruit 要同时修改，读取 excle 的方法
        """
        print 'excel arrange data ....'
        self.dml_obj = oracle()
        self.createFolder()
        # self.closeOpen()

        # self.arrangeEmployee()    # 每天    員工信息
        # self.insertDemand()    # 每天    人力需求
        # self.insertRecruit()    # 每天    招募情況
        # self.insertCrd()    # 每天    刷卡記錄
        # self.insertDimission()    # 每天    離職
        # self.insertattendanceanomaly()    #每天    陆干考勤異常
        # self.insertpzmsattendanceanomaly() #每天    台干考勤異常
        # self.insert_attendance_history()    #每天    陆干考勤異常历史
        # self.insert_PZMS_attendance_history() #每天    台干考勤異常历史
        # self.insertfalseattendance()    #每天    虛報出勤
        # self.insertemail()    #每 周两次   員工郵箱信息
        # self.insertEHumans()    # 每天    時實人力狀況/天
        # self.insertPZMS()       # 臺幹刷卡記錄

        # self.insertLMFCrd()       # 刷卡記錄
        # self.insertWeekCrd()       # 陆幹每周刷卡記錄
        # self.insertWeekPZMS()       # 臺幹每周刷卡記錄
        # self.insertLMFPZMS()       # 臺幹刷卡記錄
        # self.insertExcel()   # 每日执行,在EAMP爬虫后执行
        # self.insert_golden_stone_project()
        self.insert_egspbyleader()
        # self.insert_etravel()
        # self.insert_travel_count()
        # self.insert_register_project()

    def insertLMFCrd(self):
        """
        @note: 
        """
        self.file_object.write("\n ---------------------LMFCrd 刷卡信息----------------------- \n")
        self.writeTxt("insert LMFCrd 刷卡信息", "Beginning")
        crd_path = self.getCrdPath(GeneralParameters.lmf_crd_xls)
        all_crd_file_list = os.listdir(crd_path)
        self.writeTxt("insert LMFCrd 刷卡信息", "Excel文件有'" + str(len(all_crd_file_list)) + "'个")
        yesterday = datetime.strptime(str(datetime.now()).split(" ")[0] + " 00:00:00", '%Y-%m-%d %H:%M:%S') - timedelta(
            days=1)
        # 测试
        # yesterday = datetime.strptime('2019-08-21 00:00:00', '%Y-%m-%d %H:%M:%S') - timedelta(days=1)
        # 数据存在判断
        if self.dml_obj.selectData("c_id", GeneralParameters.lmf_crd_table,
                                   "c_datetime =to_date('%s','yyyy-mm-dd hh24:mi:ss')" % yesterday):
            print " 已存在 该日期资料"
            print "----- Finished insert crd_table!!"
            self.writeTxt("insert LMFCrd 刷卡信息", "资料已存在，不需写入数据库")
            return

        for each_file_name in all_crd_file_list:
            each_xls_path = os.path.join(crd_path, each_file_name)
            if not each_xls_path:
                self.writeTxt("insert LMFCrd 刷卡信息", "没有 Excel文件")
                self.writeTxt("insert LMFCrd 刷卡信息", "Finished")
                continue

            crd_data = self.getCsvData(each_xls_path)
            if crd_data:
                crd_data = self.deleteCrdData(crd_data)
                crd_data = self.forDateField(crd_data, [3], "%Y/%m/%d")
                crd_data = self.forDateField(crd_data, [8, 10], "%Y/%m/%d %H:%M:%S")

                this_crd_time = str(crd_data[0][3])

                # 判断数据是昨天 就插入
                if str(yesterday) == this_crd_time:
                    self.insertExcept(crd_data, GeneralParameters.lmf_crd_order_string, GeneralParameters.lmf_crd_table,
                                      "insert LMFCrd 刷卡信息")
                else:
                    # 否则就是前天的 删除后插入
                    lmf_crd_sql = "c_datetime = to_date('" + this_crd_time + "', 'yyyy-mm-dd hh24:mi:ss')"
                    self.dml_obj.deleteData(GeneralParameters.lmf_crd_table, lmf_crd_sql)
                    self.insertExcept(crd_data, GeneralParameters.lmf_crd_order_string, GeneralParameters.lmf_crd_table,
                                      "insert LMFCrd 刷卡信息")
            else:
                self.writeTxt("insert LMFCrd 刷卡信息", "Excel文件中没有数据")
        logging.info("Finished insertLMFCrd!!")
        self.writeTxt("insert LMFCrd 刷卡信息", "Finished")

    def insertWeekCrd(self):
        """
        @note: 每週一 開始刷 上週考勤數據
        """
        self.file_object.write("\n ---------------------WeekCrd 刷卡信息----------------------- \n")
        self.writeTxt("insert WeekCrd 刷卡信息", "Beginning")
        crd_path = self.getCrdPath(GeneralParameters.week_crd_xls)
        all_crd_file_list = os.listdir(crd_path)
        self.writeTxt("insert WeekCrd 刷卡信息", "Excel文件有'" + str(len(all_crd_file_list)) + "'个")
        week_first_day = datetime.strptime(str(datetime.now()).split(" ")[0] + " 00:00:00",
                                           '%Y-%m-%d %H:%M:%S') - timedelta(
            days=7)
        # 测试
        # week_first_day = datetime.strptime('2019-08-21 00:00:00', '%Y-%m-%d %H:%M:%S') - timedelta(days=1)

        for each_file_name in all_crd_file_list:
            each_xls_path = os.path.join(crd_path, each_file_name)
            if not each_xls_path:
                self.writeTxt("insert WeekCrd 刷卡信息", "没有 Excel文件")
                self.writeTxt("insert WeekCrd 刷卡信息", "Finished")
                continue

            crd_data = self.getCsvData(each_xls_path)
            if crd_data:
                crd_data = self.deleteCrdData(crd_data)
                crd_data = self.forDateField(crd_data, [3], "%Y/%m/%d")
                crd_data = self.forDateField(crd_data, [8, 10], "%Y/%m/%d %H:%M:%S")

                # 删除上周数据
                #  删除后插入
                week_crd_sql = "c_datetime >= to_date('" + str(week_first_day) + "', 'yyyy-mm-dd hh24:mi:ss')"
                self.dml_obj.deleteData(GeneralParameters.lmf_crd_table, week_crd_sql)
                self.insertExcept(crd_data, GeneralParameters.lmf_crd_order_string, GeneralParameters.lmf_crd_table,
                                  "insert LMFCrd 刷卡信息")
            else:
                self.writeTxt("insert WeekCrd 刷卡信息", "Excel文件中没有数据")
        logging.info("Finished insertLMFCrd!!")
        self.writeTxt("insert WeekCrd 刷卡信息", "Finished")

    def insertWeekPZMS(self):
        """
        @note: 每週一 開始刷 上週台干考勤數據
        """
        self.file_object.write("\n ---------------------WeekPZMS 台干刷卡资料----------------------- \n")
        self.writeTxt("insert WeekPZMS 台干刷卡资料", "Beginning")
        crd_path = self.getCrdPath(GeneralParameters.week_pzms_xls)
        all_crd_file_list = os.listdir(crd_path)
        self.writeTxt("insert WeekCrd 刷卡信息", "Excel文件有'" + str(len(all_crd_file_list)) + "'个")

        # 测试
        # week_first_day = datetime.strptime('2019-08-21 00:00:00', '%Y-%m-%d %H:%M:%S') - timedelta(days=1)
        for each_file_name in all_crd_file_list:
            each_xls_path = os.path.join(crd_path, each_file_name)
            if not each_xls_path:
                self.writeTxt("insert WeekFPZMS 台干刷卡资料", "没有 Excel文件")
                self.writeTxt("insert WeekPZMS 台干刷卡资料", "Finished")
                continue

            pams_data = self.getXlsData(each_xls_path)

            if pams_data:
                crd_data = self.getPzmsData(pams_data)
                crd_data = self.forDateField(crd_data[1:], [1], "%Y/%m/%d")
                crd_data = self.forPzmsDateField(crd_data, [7, 9], "%Y/%m/%d %H:%M")

                # 中干函数中已经删除了, 所以不需要判断了
                self.insertExcept(crd_data, GeneralParameters.lmf_pzms_order_string, GeneralParameters.lmf_crd_table,
                                  "insert WeekPZMS台干刷卡资料")
                logging.info("Finished insertWeekPZMS!!")
            else:
                self.writeTxt("insert WeekPZMS 台干刷卡资料", "Excel文件中没有数据")
            self.writeTxt("insert WeekPZMS 台干刷卡资料", "Finished")

    def insertLMFPZMS(self):
        """
        @note: 
        """
        self.file_object.write("\n ---------------------LMFPZMS 台干刷卡资料----------------------- \n")
        self.writeTxt("insert LMFPZMS 台干刷卡资料", "Beginning")
        crd_path = self.getCrdPath(GeneralParameters.lmf_pzms_xls)
        all_crd_file_list = os.listdir(crd_path)

        for each_file_name in all_crd_file_list:
            each_xls_path = os.path.join(crd_path, each_file_name)
            if not each_xls_path:
                self.writeTxt("insert LMFPZMS 台干刷卡资料", "没有 Excel文件")
                self.writeTxt("insert LMFPZMS 台干刷卡资料", "Finished")
                continue

            pams_data = self.getXlsData(each_xls_path)

            if pams_data:
                crd_data = self.getPzmsData(pams_data)
                crd_data = self.forDateField(crd_data[1:], [1], "%Y/%m/%d")
                crd_data = self.forPzmsDateField(crd_data, [7, 9], "%Y/%m/%d %H:%M")

                this_crd_time = str(crd_data[0][1])
                exist_crd_sql = "c_datetime = to_date('" + this_crd_time + "','yyyy-mm-dd hh24:mi:ss')" + \
                                " and eemployee_id = '" + crd_data[0][0] + "'"
                if self.dml_obj.selectData("c_id", GeneralParameters.lmf_crd_table, exist_crd_sql):
                    print " 已存在 该日期资料"
                    print "----- Finished insert crd_table!!"
                    self.writeTxt("insert LMFPZMS 台干刷卡资料", "资料已存在，不需写入数据库")
                    continue
                # 中干函数中已经删除了, 所以不需要判断了
                self.insertExcept(crd_data, GeneralParameters.lmf_pzms_order_string, GeneralParameters.lmf_crd_table,
                                  "insert LMFPZMS台干刷卡资料")
                logging.info("Finished insertLMFPZMS!!")
            else:
                self.writeTxt("insert LMFPZMS 台干刷卡资料", "Excel文件中没有数据")
            self.writeTxt("insert LMFPZMS 台干刷卡资料", "Finished")

    def insertPZMS(self):
        self.file_object.write("\n ---------------------PZMS 台干刷卡资料----------------------- \n")
        self.writeTxt("insert PZMS 台干刷卡资料", "Beginning")
        crd_path = self.getXlsPath(GeneralParameters.pams_xls)
        if not crd_path:
            self.writeTxt("insert PZMS 台干刷卡资料", "没有 Excel文件")
            self.writeTxt("insert PZMS 台干刷卡资料", "Finished")
            return

        pams_data = self.getXlsData(crd_path)

        if pams_data:
            crd_data = self.getPzmsData(pams_data)
            crd_data = self.forDateField(crd_data[1:], [1], "%Y/%m/%d")
            crd_data = self.forPzmsDateField(crd_data, [7, 9], "%Y/%m/%d %H:%M")

            this_crd_time = str(crd_data[0][1])
            exist_crd_sql = "c_datetime = to_date('" + this_crd_time + "','yyyy-mm-dd hh24:mi:ss')" + \
                            " and eemployee_id = '" + crd_data[0][0] + "'"
            if self.dml_obj.selectData("c_id", GeneralParameters.crd_table, exist_crd_sql):
                print " 已存在 该日期资料"
                print "----- Finished insert crd_table!!"
                self.writeTxt("insert PZMS 台干刷卡资料", "资料已存在，不需写入数据库")
                return
            self.insertExcept(crd_data, GeneralParameters.pzms_order_string, GeneralParameters.crd_table,
                              "insert PZMS台干刷卡资料")
            logging.info("Finished insertPZMS!!")
        else:
            self.writeTxt("insert PZMS 台干刷卡资料", "Excel文件中没有数据")
        self.writeTxt("insert PZMS 台干刷卡资料", "Finished")

    def insertEHumans(self):
        '''
        @note: 'h_cname, h_num, h_ename, h_group, h_team, h_taiwan, h_mesome, h_technician, h_spindrift'
        @note: '主管, 主管工號, 主管英文名, 部長/Group, Function team, 臺干人數, 中干人數, 員級人數, 浪花人數'
        '''
        self.file_object.write("\n ---------------------EHumans 实时人力----------------------- \n")
        self.writeTxt("insert EHumans实时人力", "Beginning")
        humans_dic = self.getHumansData()

        humans_list_data = []
        for key, value in humans_dic.items():
            this_list = []
            this_manager_id = value[0]
            this_manager_team = key
            this_manager_cname_list = self.getList("e_cname", GeneralParameters.employee_table, "e_id", this_manager_id)
            this_manager_ename_list = self.getList("e_ename", GeneralParameters.employee_table, "e_id", this_manager_id)

            # 臺干人數
            taiwan_where_sql = "e_functionteam='" + this_manager_team + "' and " + \
                               "e_status='" + u"在職" + "' and " + \
                               "e_difference='" + u"臺幹" + "'"
            taiwan_man_list_len = self.getListLen("e_id", GeneralParameters.employee_table, taiwan_where_sql)

            # 中干人數 = 師級   不含 臺幹
            mesome_where_sql = "e_functionteam='" + this_manager_team + "' and " + \
                               "e_difference like '%" + u"中" + "%' and " + \
                               "e_status='" + u"在職" + "' and " + \
                               "e_grade like '%" + u"師" + "%'" + \
                               " and e_category = '" + u"常設" + "'"
            mesome_man_list_len = self.getListLen("e_id", GeneralParameters.employee_table, mesome_where_sql)

            # 員級人數 technician
            technician_where_sql = "e_functionteam='" + this_manager_team + "' and " + \
                                   "e_status='" + u"在職" + "' and " + \
                                   "e_grade like '%" + u"員" + "%'" + \
                                   " and e_category = '" + u"常設" + "'"
            technician_man_list_len = self.getListLen("e_id", GeneralParameters.employee_table, technician_where_sql)

            # 浪花人數 spindrift
            db_now_time = datetime.now().replace(second=0, microsecond=0)
            spindrift_where_sql = "e_leader='" + this_manager_ename_list[0] + "' and " + \
                                  "e_functionteam='" + this_manager_team + "' and " + \
                                  "e_status='" + u"在職" + "' and " + \
                                  "(e_expiringdate > to_date('" + str(
                db_now_time) + "','yyyy-mm-dd hh24:mi:ss') or e_expiringdate is null) and " + \
                                  "e_category != '" + u"常設" + "'"
            # print this_manager_team
            spindrift_man_list_len = self.getListLen("e_id", GeneralParameters.employee_table, spindrift_where_sql)

            this_list.append(this_manager_cname_list[0])
            this_list.append(this_manager_id)
            this_list.append(this_manager_ename_list[0])
            this_list.append(value[1])
            this_list.append(value[2])
            this_list.append(taiwan_man_list_len)
            this_list.append(mesome_man_list_len)
            this_list.append(technician_man_list_len)
            this_list.append(spindrift_man_list_len)
            humans_list_data.append(this_list)

        if humans_list_data:
            self.dml_obj.emptyTable(GeneralParameters.humans_table)
            self.insertExcept(humans_list_data, GeneralParameters.humans_order_string, GeneralParameters.humans_table,
                              "insert EHumans实时人力")
            logging.info("Finished insertEHumans!!")
            print "----- Finished insertEHumans!!"
        else:
            self.writeTxt("insert EHumans实时人力", "No Datas")
        self.writeTxt("insert EHumans实时人力", "Finished")

    def getHumansData(self):
        '''
        @note: 
        '''
        humans_dic = {}
        managers_tup = self.dml_obj.selectData("e_id", GeneralParameters.employee_table, "e_ename is not null")
        managers_list = [code_tupe[0] for code_tupe in managers_tup]
        for each_managers in managers_list:
            #             print "each_managers:",each_managers
            department_list = self.getList("d_id", GeneralParameters.department_table, "d_leadernum", each_managers)
            #             print "department_list:",department_list

            for each_department in department_list:
                each_department = str(each_department)
                group_list = self.getList("l_group", GeneralParameters.leader_table, "edepartment_id", each_department)
                #                 print "group_list:",group_list

                leader_list = self.getList("l_id", GeneralParameters.leader_table, "edepartment_id", each_department)
                #                 print "leader_list:",leader_list

                leader_val = str(leader_list[0])
                team_list = self.getList("t_team", GeneralParameters.team_table, "eleader_id", leader_val)
                #                 print "team_list:",team_list

                for each_team in team_list:
                    if each_team in humans_dic.keys():
                        continue
                    else:
                        this_list = []
                        this_list.append(each_managers)
                        this_list.append(group_list[0])
                        this_list.append(each_team)
                        humans_dic[each_team] = this_list
                    #             print "-----------------"

        return humans_dic

    def getList(self, DB_code, table_name, this_keyword_name=None, this_keyword_val=None):
        '''
        @note: 解析从数据库获得元组，分解成列表
        '''
        if this_keyword_name:
            tup_list = self.dml_obj.selectData(DB_code, table_name, this_keyword_name + " = '" + this_keyword_val + "'")
        else:
            tup_list = self.dml_obj.selectData(DB_code, table_name)
        db_code_list = [code_tupe[0] for code_tupe in tup_list]

        return db_code_list

    def getListLen(self, DB_code, table_name, where_sql):
        '''
        @note: 解析从数据库获得元组，分解成列表
        '''
        tup_list = self.dml_obj.selectData(DB_code, table_name, where_sql)
        db_code_list = [code_tupe[0] for code_tupe in tup_list]
        this_len = len(db_code_list)

        return this_len

    def arrangeEmployee(self):
        self.file_object.write("\n ---------------------Employee 员工信息----------------------- \n")
        self.writeTxt("insert Employee员工信息", "Beginning")
        employee_path = self.getXlsPath(GeneralParameters.employee_xls)
        if not employee_path:
            self.writeTxt("insert Employee员工信息", "没有 Excel文件")
            self.writeTxt("insert Employee员工信息", "Finished")
            return

        list_data = self.getXlsData(employee_path)

        print "list_data:", len(list_data)
        if list_data:
            all_rows_datas = []
            Bureau_leader = []  # 获得 处长
            Deputy_list = []
            Employee_data_list = []  # 人員
            Deputy_data_list = []  # 副職
            Bureau_data_list = []  # 處
            Department_data_list = []  # 部
            Subject_data_list = []  # 課
            Bureau_data_dic = {}  # 處
            Department_data_dic = {}  # 部
            Subject_data_dic = {}  # 課

            try:
                for row, each_row in enumerate(list_data):
                    if row >= 2:
                        # 首先过滤掉 工号含有 'TMP'以及资位是 '無' 的员工
                        if 'TMP' in each_row[1] or each_row[3] == u'無' or each_row[3] == u'无':
                            self.writeTxt("insert Employee员工信息", "过滤掉'" + each_row[1].encode('utf-8') + "',不能插入数据库")
                            continue
                        all_rows_datas.append(each_row)
                        Deputy_list.append(each_row[15:])
                        for col, each_data in enumerate(each_row):
                            each_data = each_data.encode("utf-8")
                            if each_row[10] == u" " and each_row[11] == u" " and each_row[14] == u"Y":
                                if each_row[2] not in Bureau_leader:
                                    Bureau_leader.append(each_row[2])

            except Exception as e:
                self.writeTxt("失败的原因", str(e))
                print ' list_data  error:', e
            # 判断是否 是空的列表(不是很精确，excle不知道有多少行)
            if len(Bureau_leader) < 1:
                print "------ 空的 Excel"
                self.writeTxt("insert Employee员工信息", "Excel文件中没有数据")
                return ""

            # 整理 处 部 课 三个数据库表所需要的资料
            get_Bureau_dic, get_Department_dic, get_Subject_dic, all_managements_list = self.getThreeData(
                all_rows_datas, Bureau_leader)
            Bureau_data_dic = dict(Bureau_data_dic, **get_Bureau_dic)
            Department_data_dic = dict(Department_data_dic, **get_Department_dic)
            Subject_data_dic = dict(Subject_data_dic, **get_Subject_dic)

            # 最终数据库能吃得
            Bureau_data_list, Department_data_list, Subject_data_list = self.arrageThreeData(Bureau_data_dic,
                                                                                             Department_data_dic,
                                                                                             Subject_data_dic)

            # 整理 副职 表
            Deputy_data_list = self.getDeputyData(all_rows_datas, Deputy_list)

            # 整理 員工信息 表 只含自动部分信息
            Employee_data_list, Employee_id_list = self.getEmployeeData(all_rows_datas, all_managements_list)

            # 插入 bureau_table
            self.insertBureau(Bureau_data_list)

            # 插入 department_table
            self.insertDepartment(Department_data_list)

            # 插入 subject_table
            self.insertSubject(Subject_data_list)

            # 　判断离职
            unique_list = self.dml_obj.selectData("e_id", GeneralParameters.employee_table,
                                                  "e_status='" + u"在職" + "'")
            if unique_list:
                db_code_list = [code_tupe[0] for code_tupe in unique_list]
                print "db_code_list:", len(db_code_list)
                now_time = str(datetime.now())
                #                 now_time = "2018-03-14 15:00:00"
                now_time = now_time.split(" ")[0] + " " + "00:00:00"
                for each_exist_id in db_code_list:
                    if each_exist_id not in Employee_id_list:
                        # 已离职的
                        sql_string = 'update ' + GeneralParameters.employee_table + " set e_status='" + u"離職" + \
                                     "',e_lastdate= to_date('" + now_time + "','yyyy-mm-dd hh24:mi:ss')" + \
                                     " where e_id='" + each_exist_id + "'"
                        # print "sql_string:",sql_string
                        self.dml_obj.updateData(sql_string)
            # 判斷是否離職再入職
            rehire_list = self.dml_obj.selectData("e_id", GeneralParameters.employee_table,
                                                  "e_status='" + u"離職" + "'")
            if rehire_list:
                db_code_list = [code_tupe[0] for code_tupe in rehire_list]
                print "db_code_list:", len(db_code_list)
                now_time = str(datetime.now())
                #                 now_time = "2018-03-14 15:00:00"
                now_time = now_time.split(" ")[0] + " " + "00:00:00"
                for each_exist_id in db_code_list:
                    if each_exist_id in Employee_id_list:
                        # 已离职的
                        sql_string = 'update ' + GeneralParameters.employee_table + " set e_status='" + u"在職" + \
                                     "',e_lastdate= to_date('" + now_time + "','yyyy-mm-dd hh24:mi:ss')" + \
                                     " where e_id='" + each_exist_id + "'"
                        # print "sql_string:",sql_string
                        self.dml_obj.updateData(sql_string)

            # 插入 employee_table
            self.insertEmployee(Employee_data_list)
            # 插入 deputy_table
            self.insertDeputy(Deputy_data_list)
            """2019-06-17 changed part:new function add_E_firsrdate """
            # 將五月后新建且e_firstdate值為null的數據設置e_firstdate的值等於create_time
            self.add_E_firsrdate()
        else:
            self.writeTxt("insert Employee员工信息", "Excel文件中没有数据")
        self.writeTxt("insert Employee 员工信息", "Finished")

    def getThreeData(self, all_data, Bureau_leader):
        """
        @note: 整理 处 部 课  三个表
        """
        Bureau_dic = {}  # 處
        Department_dic = {}  # 部
        Subject_dic = {}  # 課
        Subject_list = []  # 課
        department_list = []  # 部 名称
        managements_list = []  # 部长 名字
        managements_id_list = []  # 部长 工号
        all_managements_list = []

        for row, row_data in enumerate(all_data):
            # 获得 处级单位
            if row_data[6] == u"處長":
                man_id = [str(row_data[1]), row_data[2], row_data[8]]
                this_bureau = row_data[8]
                if this_bureau not in Bureau_dic.keys():
                    Bureau_dic[this_bureau] = man_id

            # 获得 直屬主管 是 高易韜 的 所有部长,部长还有在课级单位中
            if row_data[7] in Bureau_leader:
                man_id = [str(row_data[1]), row_data[2], row_data[8]]
                this_department = row_data[10]
                Department_dic[this_department] = man_id
                department_list.append(this_department)
                managements_list.append(row_data[2])
                managements_id_list.append(str(row_data[1]))

            if row_data[11] and row_data[14] == "Y":
                Subject_list.append(row_data)  # 還需整理

            # 获得 課 (由于有的课级单位，课长没标明)，还包含部分部长
            if row_data[11] and row_data[11] not in Subject_dic:
                #                 if row_data[14] == "Y":
                #                     man_id = [str(row_data[1]), row_data[2], row_data[10]]
                #                 else:
                #                     man_id = ["", "", row_data[10]]
                man_id = [str(row_data[1]), row_data[2], row_data[10]]
                Subject_dic[row_data[11]] = man_id

        # 获得 完整的部
        for row_data in Subject_list:
            if row_data[7] in managements_list:
                if row_data[10] not in department_list:
                    this_department = row_data[10]
                    index_id = managements_list.index(row_data[7])
                    man_id = [managements_id_list[index_id], managements_list[index_id], row_data[8]]
                    Department_dic[this_department] = man_id
                    department_list.append(this_department)

        # 获得 完整的课
        for keys, values in Subject_dic.items():
            if values[0] in managements_id_list:
                Subject_dic.pop(keys)
            # 杨真健 修改他的归属部门
            if values[0] == 'F1226256':
                values[2] = u"iDPBG EERF 系統部_觀瀾"
            # 修改jay 歸屬部門   認證規範部_觀瀾
            if values[0] == '22937':
                values[2] = u"iDPBG EERF 認證規範部_觀瀾"

        all_managements_list.append(managements_list)
        all_managements_list.append(managements_id_list)

        return Bureau_dic, Department_dic, Subject_dic, all_managements_list

    def arrageThreeData(self, Bureau_data_dic, Department_data_dic, Subject_data_dic):
        """
        @note: 整理 处 部 课  三个表 整理成数据库中的每一笔资料    [str(row_data[1]), row_data[2], row_data[8]]
        """
        Bureau_list = []  # 處
        Department_list = []  # 部
        Subject_list = []  # 課
        # 整理成数据库中的每一笔资料 處
        for keys, values in Bureau_data_dic.items():
            eahc_data = []
            this_values = values
            eahc_data.append(keys)
            eahc_data.append(this_values[0])
            eahc_data.append(this_values[1])
            eahc_data.append(u"NPI")
            Bureau_list.append(eahc_data)
        # 整理成数据库中的每一笔资料 部
        for keys, values in Department_data_dic.items():
            eahc_data = []
            this_values = values
            eahc_data.append(keys)
            eahc_data.append(this_values[0])
            eahc_data.append(this_values[1])
            eahc_data.append(this_values[2])
            Department_list.append(eahc_data)
        # 整理成数据库中的每一笔资料 課
        for keys, values in Subject_data_dic.items():
            eahc_data = []
            this_values = values
            eahc_data.append(keys)
            eahc_data.append(this_values[0])
            eahc_data.append(this_values[1])
            eahc_data.append(this_values[2])
            Subject_list.append(eahc_data)

        return Bureau_list, Department_list, Subject_list

    def getDeputyData(self, all_data, Deputy_list):
        """
        @note: 整理 副职 表
        """
        Deputy_dic = {}
        Deputy_data_dic = {}
        Deputy_data_list = []
        # 初步整理
        for row, row_data in enumerate(Deputy_list):
            this_row_deputy = []
            for col, each_data in enumerate(row_data):
                new_each_data = each_data.replace(" ", "")
                if col == 0 and new_each_data == "":
                    break
                else:
                    this_row_deputy.append(each_data)
            if this_row_deputy:
                man_id = str(all_data[row][1]) + "_" + all_data[row][2]
                Deputy_dic[man_id] = this_row_deputy
        # 进一步整理 去除空值 
        for keys, values in Deputy_dic.items():
            new_values = []
            len_num = len(values) / 7
            for num in range(0, len_num):
                first_num = (0 + num) * 7
                last_num = (1 + num) * 7
                for r, v in enumerate(values[first_num:last_num]):
                    new_v = v.replace(" ", "")
                    if r == 0 and v == "":
                        break
                    elif r == 0 and new_v:
                        this_new_values = values[first_num:last_num]
                        new_values.append(this_new_values)
                        break
            Deputy_data_dic[keys] = new_values
        # 整理成数据库中的每一笔资料
        for keys, values in Deputy_data_dic.items():
            this_man_id = keys.split("_")[0]
            for each_data in values:
                this_one_data = each_data
                this_one_data.insert(0, this_man_id)
                this_one_data.pop(3)
                Deputy_data_list.append(this_one_data)
        return Deputy_data_list

    def getEmployeeData(self, all_data, all_managements_list):
        """
        @note: 整理 員工信息 表 只含自动部分信息
        @note: 工號,中文名,資位,直間接,干別,管理職,直屬主管,製造處,廠/處級,部級,課級,組級,線級,DRI
        @note: 工號,密碼,中文名,資位,直間接,干別,管理職,直屬主管,
        @note: 廠區,製造處/機能處/廠處,部級,課級,組級,線級,DRI,擁有的權限,就職狀態,離廠日期
        @note: Leader， Function Team
        """
        Employee_list = []
        employee_id_list = []
        managements_list = all_managements_list[0]  # 部长 名字
        managements_id_list = all_managements_list[1]  # 部长 工号
        for row, row_data in enumerate(all_data):
            this_employee_information = row_data[1:15]
            this_employee_information.pop(8)  # 去除某个位置的元素
            this_employee_information[0] = str(row_data[1])

            # 密码
            this_employee_information.insert(1, str(row_data[1]))

            # 厂区
            if row_data[10]:
                this_employee_place = row_data[10].split("_")[-1]
            if row_data[10] == u" " and row_data[11] == u" " and row_data[14] == u"Y":
                this_employee_place = u"觀瀾"

            if this_employee_place == u"觀瀾":
                this_employee_place = "GL"
            elif this_employee_place == u"鄭州":
                this_employee_place = "ZZ"
            else:
                this_employee_place = "GL"
            this_employee_information.insert(8, this_employee_place)

            # 就職狀態
            if row_data[6] == u"處長":
                this_employee_authority = u"處長"
            elif row_data[1] in managements_id_list:
                this_employee_authority = u"部長"
            elif row_data[7] in managements_list and row_data[14] == 'Y':
                this_employee_authority = u"課長"
            else:
                this_employee_authority = u"員工"
            this_employee_information.insert(15, this_employee_authority)

            # 擁有的權限
            this_employee_status = u"在職"
            this_employee_information.insert(16, this_employee_status)

            # 離廠日期
            this_employee_lastdate = u""
            this_employee_information.insert(17, this_employee_lastdate)

            Employee_list.append(this_employee_information)
            employee_id_list.append(this_employee_information[0])
        return Employee_list, employee_id_list

    def insertBureau(self, Bureau_data_list):
        self.file_object.write("\n ---------------------Bureau 处级单位----------------------- \n")
        insert_bureau_data, update_bureau_data = self.getInsertData("b_bureau", GeneralParameters.bureau_table,
                                                                    Bureau_data_list, 0)
        for each_update_list in update_bureau_data:
            if each_update_list:
                sql_string = 'update ' + GeneralParameters.bureau_table + " set b_bureau='" + each_update_list[0] + \
                             "',b_leadernum='" + each_update_list[1] + "',b_leader='" + each_update_list[2] + \
                             "',b_up='" + each_update_list[3] + "' where b_bureau='" + each_update_list[0] + "'"
                self.dml_obj.updateData(sql_string)
        logging.info("Finished update_bureau_data!!")
        if insert_bureau_data:
            self.insertExcept(insert_bureau_data, GeneralParameters.bureau_order_string, GeneralParameters.bureau_table,
                              "insert Bureau处级单位")
            logging.info("Finished insert_bureau_data!!")
        self.writeTxt("insert Bureau处级单位", "插入数据 与 修改数据 完成")

    def insertDepartment(self, Department_data_list):
        self.file_object.write("\n ---------------------Department 部级单位----------------------- \n")
        insert_depart_data, update_depart_data = self.getInsertData("d_department", GeneralParameters.department_table,
                                                                    Department_data_list, 0)
        #         self.printData(update_depart_data[:1])
        for each_update_list in update_depart_data:
            if each_update_list:
                bureau_val = each_update_list[3]
                bureau_pk = self.getFK("b_id", "b_bureau", bureau_val, GeneralParameters.bureau_table)
                bureau_pk = str(bureau_pk)
                sql_string = 'update ' + GeneralParameters.department_table + " set d_department='" + each_update_list[
                    0] + \
                             "',d_leadernum='" + each_update_list[1] + "',d_leader='" + each_update_list[2] + \
                             "',ebureau_id='" + bureau_pk + "' where d_department='" + each_update_list[0] + "'"
                self.dml_obj.updateData(sql_string)
        logging.info("Finished update_depart_data!!")
        for each_list in insert_depart_data:
            bureau_val = each_list[3]
            bureau_pk = self.getFK("b_id", "b_bureau", bureau_val, GeneralParameters.bureau_table)
            each_list[3] = bureau_pk

        if insert_depart_data:
            self.insertExcept(insert_depart_data, GeneralParameters.department_order_string,
                              GeneralParameters.department_table, "insert Department部级单位")
            logging.info("Finished insert_depart_data!!")
        self.writeTxt("insert Department部级单位", "插入数据 与 修改数据 完成")

    def insertSubject(self, Subject_data_list):
        self.file_object.write("\n ---------------------Subject 课级单位----------------------- \n")
        insert_subject_data, update_subject_data = self.getInsertData("s_subject", GeneralParameters.subject_table,
                                                                      Subject_data_list, 0)
        #         self.printData(update_subject_data[:1])
        for each_update_list in update_subject_data:
            if each_update_list:
                depart_val = each_update_list[3]
                depart_pk = self.getFK("d_id", "d_department", depart_val, GeneralParameters.department_table)
                if depart_pk is not None:
                    depart_pk = str(depart_pk)
                    sql_string = 'update ' + GeneralParameters.subject_table + " set s_subject='" + each_update_list[
                        0] + \
                                 "',s_leadernum='" + each_update_list[1] + "',s_leader='" + each_update_list[2] + \
                                 "',edepartment_id='" + depart_pk + "' where s_subject='" + each_update_list[0] + "'"
                    self.dml_obj.updateData(sql_string)
        logging.info("Finished update_subject_data!!")
        for each_list in insert_subject_data:
            depart_val = each_list[3]
            depart_pk = self.getFK("d_id", "d_department", depart_val, GeneralParameters.department_table)
            each_list[3] = depart_pk

        if insert_subject_data:
            self.insertExcept(insert_subject_data, GeneralParameters.subject_order_string,
                              GeneralParameters.subject_table, "insert Subject课级单位")
            logging.info("Finished insert_subject_data!!")
        self.writeTxt("insert Subject课级单位", "插入数据 与 修改数据 完成")

    def insertEmployee(self, Employee_data_list):
        '''
        @note: 
        '''
        self.file_object.write("\n ---------------------Employee 员工信息----------------------- \n")
        # 获取英文名的 leader （手动资料必须已插入）
        leader_dic = {}
        depart_tup = self.dml_obj.selectData("e_id,e_ename", GeneralParameters.employee_table, "e_ename is not null")

        if depart_tup:
            for each_tup in depart_tup:
                # 去除 单江锋
                if each_tup[0] != "F1202542":
                    leader_dic[each_tup[0]] = each_tup[1]

        insert_employee_data, update_employee_data = self.getEmployeeInsertData("e_id",
                                                                                GeneralParameters.employee_table,
                                                                                Employee_data_list, 0)

        self.updateEmployee(update_employee_data, leader_dic)
        logging.info("Finished update_employee_data!!")

        new_insert_employee_data = []
        for each_list in insert_employee_data:
            bureau_val = each_list[9]
            bureau_pk = self.getFK("b_id", "b_bureau", bureau_val, GeneralParameters.bureau_table)
            each_list[9] = bureau_pk

            depart_val = each_list[10]
            depart_pk = self.getFK("d_id", "d_department", depart_val, GeneralParameters.department_table)
            each_list[10] = depart_pk

            subject_val = each_list[11]
            subject_pk = self.getFK("s_id", "s_subject", subject_val, GeneralParameters.subject_table)
            each_list[11] = subject_pk

            group_val = each_list[12]
            group_pk = self.getFK("g_id", "g_group", group_val, GeneralParameters.group_table)
            each_list[12] = group_pk

            line_val = each_list[13]
            line_pk = self.getFK("l_id", "l_line", line_val, GeneralParameters.line_table)
            each_list[13] = line_pk

            this_new_list = each_list

            # 获取 functionTeam
            if each_list[15] == u"處長":
                functionTeam_val = ""
            elif each_list[15] == u"部長":
                subject_tup = self.dml_obj.selectData("s_subject", GeneralParameters.subject_table,
                                                      "edepartment_id='%s'" % depart_pk)
                if subject_tup:
                    subject_name = subject_tup[0][0]
                    subject_tup = self.dml_obj.selectData("st_team", GeneralParameters.subject_team_table,
                                                          "st_subject='%s'" % subject_name)
                    if subject_tup and each_list[8] == "GL":
                        functionTeam_val = subject_tup[0][0]
                    else:
                        functionTeam_val = ""
                else:
                    functionTeam_val = ""
            else:
                subject_tup = self.dml_obj.selectData("st_team", GeneralParameters.subject_team_table,
                                                      "st_subject='%s'" % subject_val)
                if subject_tup and each_list[8] == "GL":
                    functionTeam_val = subject_tup[0][0]
                else:
                    functionTeam_val = ""

            # 获取 英文名的 leader
            # if depart_pk and leader_dic:
            if leader_dic:
                if subject_tup and each_list[8] == "GL":
                    leader_id_tup = self.dml_obj.selectData("eleader_id", GeneralParameters.team_table,
                                                            "t_team='%s'" % subject_tup[0][0])
                    edepartment_id_tup = self.dml_obj.selectData("edepartment_id", GeneralParameters.leader_table,
                                                                 "l_id='%s'" % leader_id_tup[0][0])
                    d_leadernum_tup = self.dml_obj.selectData("d_leadernum", GeneralParameters.department_table,
                                                              "d_id='%s'" % edepartment_id_tup[0][0])
                    leader_name = leader_dic[d_leadernum_tup[0][0]]
                else:
                    leader_name = ""
            else:
                leader_name = ""

            this_new_list.append(leader_name)
            this_new_list.append(functionTeam_val)
            new_insert_employee_data.append(this_new_list)
        if new_insert_employee_data:
            self.insertExcept(new_insert_employee_data, GeneralParameters.employee_auto_order_string,
                              GeneralParameters.employee_table, "insert Employee员工信息")
            logging.info("Finished insert_employee_data!!")
        self.writeTxt("insert Employee员工信息", "插入数据 与 修改数据 完成")

    def updateEmployee(self, update_employee_data, leader_dic):
        '''
        @note: 
        '''
        for each_update_list in update_employee_data:
            if each_update_list:
                e_category = '常設'
                if '浪花' in each_update_list[11]:
                    e_category = '支援'

                # 製造處/機能處/廠處
                bureau_val = each_update_list[9]
                bureau_pk = self.getUpdateFK("b_id", "b_bureau", bureau_val, GeneralParameters.bureau_table)

                # 部級,根据10的部及名称去edepartment表获取d_id,d_department
                depart_val = each_update_list[10]
                depart_pk = self.getUpdateFK("d_id", "d_department", depart_val, GeneralParameters.department_table)

                # 课级
                subject_val = each_update_list[11]
                subject_pk = self.getUpdateFK("s_id", "s_subject", subject_val, GeneralParameters.subject_table)
                # 修改jay的主管 
                if subject_val == u"iDPBG EERF FATP 軟件開發課_觀瀾":
                    depart_pk = self.getUpdateFK("edepartment_id", "s_subject", subject_val,
                                                 GeneralParameters.subject_table)
                    if each_update_list[0] == "22937":
                        each_update_list[7] = u"張銘棋"

                group_pk = ""

                line_pk = ""
                # 年资
                this_seniority_val = self.getSeniority(each_update_list[0])
                # 获取 functionTeam
                if each_update_list[15] == u"處長":
                    functionTeam_sql_str = ""
                    subject_tup = ""
                elif each_update_list[15] == u"部長":
                    # todo::获取课级数据
                    subject_tup = self.dml_obj.selectData("s_subject", GeneralParameters.subject_table,
                                                          "edepartment_id='%s'" % depart_pk)
                    if subject_tup:
                        # 课级名称
                        subject_name = subject_tup[0][0]
                        # functionTeam
                        subject_tup = self.dml_obj.selectData("st_team", GeneralParameters.subject_team_table,
                                                              "st_subject='%s'" % subject_name)
                        if subject_tup and each_update_list[8] == "GL":  # 观澜
                            functionTeam_sql_str = ",e_functionteam='%s'" % subject_tup[0][0]
                        else:  # 郑州的
                            functionTeam_sql_str = ""
                    else:  # 没有获取到 subject_tup
                        functionTeam_sql_str = ""

                else:  # 员工部分
                    subject_tup = self.dml_obj.selectData("st_team", GeneralParameters.subject_team_table,
                                                          "st_subject='%s'" % subject_val)
                    if subject_tup:
                        if subject_tup and each_update_list[8] == "GL":
                            functionTeam_sql_str = ",e_functionteam='%s'" % subject_tup[0][0]
                        else:
                            functionTeam_sql_str = ""
                    else:
                        functionTeam_sql_str = ""

                # 获取 英文名的 leader
                # if depart_pk and leader_dic:
                if leader_dic:
                    if subject_tup and each_update_list[8] == "GL":
                        # 1.在e_team表中获取对应的eleader_id
                        leader_id_tup = self.dml_obj.selectData("eleader_id", GeneralParameters.team_table,
                                                                "t_team='%s'" % subject_tup[0][0])
                        # 2.根据上面获取的eleader_id，去eleader表获取edepartment_id
                        edepartment_id_tup = self.dml_obj.selectData("edepartment_id", GeneralParameters.leader_table,
                                                                     "l_id='%s'" % leader_id_tup[0][0])
                        # 3.根据上面获取的edepartment_id去edepartment表获取d_leadernum
                        d_leadernum_tup = self.dml_obj.selectData("d_leadernum", GeneralParameters.department_table,
                                                                  "d_id='%s'" % edepartment_id_tup[0][0])
                        # 4.最终获取到了leadername
                        leader_name = leader_dic[d_leadernum_tup[0][0]]
                        leader_name_sql_str = ",e_leader='%s'" % leader_name

                    else:
                        leader_name_sql_str = ""
                else:
                    leader_name_sql_str = ""

                sql_string = 'update ' + GeneralParameters.employee_table + " set e_cname='" + each_update_list[2] + \
                             "',e_grade='" + each_update_list[3] + "',e_direct='" + each_update_list[4] + \
                             "',e_difference='" + each_update_list[5] + "',e_management='" + each_update_list[6] + \
                             "',e_managers='" + each_update_list[7] + "',e_place='" + each_update_list[8] + \
                             "',ebureau_id='" + bureau_pk + "',edepartment_id='" + depart_pk + \
                             "',esubject_id='" + subject_pk + "',egroup_id='" + group_pk + "',e_category='" + e_category + \
                             "',eline_id='" + line_pk + "',e_DRI='" + each_update_list[14] + \
                             "',e_authority='" + each_update_list[15] + "',e_status='" + u"在職" + \
                             "',e_seniority='" + this_seniority_val + "'" + leader_name_sql_str + functionTeam_sql_str + \
                             ",e_lastdate=to_date('" + "" + "','yyyy-mm-dd hh24:mi:ss') where e_id='" + \
                             each_update_list[0] + "'"
                self.dml_obj.updateData(sql_string)

    def insertDeputy(self, Deputy_data_list):
        self.file_object.write("\n ---------------------Deputy 一人多职位----------------------- \n")
        insert_deputy_data = Deputy_data_list

        if insert_deputy_data:
            self.dml_obj.emptyTable(GeneralParameters.deputy_table)
            self.insertExcept(insert_deputy_data, GeneralParameters.deputy_order_string, GeneralParameters.deputy_table,
                              "insert Deputy一人多职位")
        else:
            self.writeTxt("insert Deputy一人多职位", "没有数据")
        self.writeTxt("insert Deputy一人多职位", "Finished")

    def insertDemand(self):
        self.file_object.write("\n ---------------------Demand 招募----------------------- \n")
        self.writeTxt("insert Demand招募", "Beginning")
        demand_path = self.getFHRPath(GeneralParameters.demand_xls)
        if not demand_path:
            self.writeTxt("insert Demand招募", "没有 Excel文件")
            self.writeTxt("insert Demand招募", "Finished")
            return

        demand_data = self.getFHRData(demand_path)
        if demand_data:
            demand_final_data = []
            demand_data = self.forDateField(demand_data[2:], [23, 24], "%Y-%m-%d")
            demand_data = self.forSubjectField(demand_data, [5])

            #             self.printData(demand_data)
            #             for row_d in demand_data:
            #                 if row_d[2] in [u'進行中',u'完成']:
            #                     demand_final_data.append(row_d)

            demand_final_data.extend(demand_data)
            # 判断是否 该单号是需要 insert_demand_data 还是 update_demand_data
            other_demand_data, delete_demand_data = self.getInsertData("d_number", GeneralParameters.demand_table,
                                                                       demand_final_data, 1)
            if demand_final_data:
                for each_delete_list in delete_demand_data:
                    self.dml_obj.deleteData(GeneralParameters.demand_table,
                                            "d_number = '{}'".format(each_delete_list[1]))
            if demand_final_data:
                self.insertExcept(demand_final_data, GeneralParameters.demand_order_string,
                                  GeneralParameters.demand_table, "insert Demand招募")
                logging.info("Finished insert_demand_data!!")

            delete_num = len(delete_demand_data)
            insert_num = len(demand_final_data)
            self.writeTxt("insert Demand招募", "刪除{}條数据  插入{}條数据".format(delete_num, insert_num))
            self.writeTxt("insert Demand招募", "刪除数据 与 插入数据 完成")
        else:
            self.writeTxt("insert Demand招募", "Excel文件中没有数据")
        self.writeTxt("insert Demand招募", "Finished")
        logging.info("Finished insertDemand!!")

    def get_extra_recruit_index(self, title):
        """从录用进度表中获取数据库ERECRUIT表的字段,防止excel表总是变化导致插入数据库失败"""
        need_column = [u'作業狀態', u'需求單號', u'姓名', u'性別', u'身份證號碼', u'聯系方式', u'面試日期', u'事業處', u'應聘單位',
                       u'應聘職位', u'需求主管1', u'需求主管2', u'簡歷來源', u'招募專員', u'學歷', u'預核資位', u'面試主管1結果',
                       u'面試主管2結果', u'簽核進度', u'體檢日期', u'體檢結果', u'報到日期', u'異常備注']
        need_index = []
        if len(title) >= len(need_column):
            for i, t in enumerate(title):
                for j, n in enumerate(need_column):
                    if n == t:
                        if i not in need_index:
                            need_index.append(i)
            return need_index
        else:
            return range(len(title))

    def insertRecruit(self):
        self.file_object.write("\n ---------------------Recruit 招募进度----------------------- \n")
        self.writeTxt("insert Recruit招募进度", "Beginning")
        recruit_path = self.getFHRPath(GeneralParameters.recruit_xls)
        if not recruit_path:
            self.writeTxt("insert Recruit招募进度", "没有 Excel文件")
            self.writeTxt("insert Recruit招募进度", "Finished")
            return

        recruit_data = self.getFHRData(recruit_path)
        # print('------recruit_data------')
        # self.printData(recruit_data[:1])

        # extra_index = 12  # 招募管道 多余的数据

        if recruit_data:
            need_index = self.get_extra_recruit_index(recruit_data[0])
            _recruit_data = []
            # 只要数据库有的字段
            for i, r in enumerate(recruit_data):
                each = []
                for j in need_index:
                    each.append(r[j])
                _recruit_data.append(each)

            recruit_final_data = []
            recruit_data = self.forDateField(_recruit_data[1:], [6, 19, 21], "%Y/%m/%d")
            recruit_final_data.extend(recruit_data)
            """ 2019/6/12 changed part begin """

            # 獲取該excel表的面試時間的年份，并轉換成字符串的形式
            final_data_year = str(recruit_final_data[0][6].year)
            # 刪除面試時間在excel表的面試時間年份內的所有信息，deleteData為新增的“刪除指定數據”方法
            self.dml_obj.deleteData(GeneralParameters.recruit_table,
                                    "R_INTERVIEW between to_date('{}-01-01','yyyy-mm-dd') and to_date('{}-12-31','yyyy-mm-dd')".format(
                                        final_data_year, final_data_year))
            # 將excel的表格中的數據插入數據庫中
            self.insertExcept(recruit_final_data, GeneralParameters.recruit_order_string,
                              GeneralParameters.recruit_table, "insert Recruit招募进度")
            logging.info("Finished insert_recruit_data!!")

            """ 2019/6/12 changed part end """
            # insert_recruit_data, update_recruit_data = self.getRecruitInsertData("r_number,r_Idcard,r_interview",
            #                                                                      GeneralParameters.recruit_table,
            #                                                                      recruit_final_data, 1)
            # if insert_recruit_data:
            #
            #     self.insertExcept(insert_recruit_data, GeneralParameters.recruit_order_string, GeneralParameters.recruit_table, "insert Recruit招募进度")
            #     logging.info("Finished insert_recruit_data!!")
            # for k, each_update_list in update_recruit_data.items():
            #     if each_update_list:
            #         if each_update_list[6] == None:
            #             each_update_list[6] = ''
            #         if each_update_list[19] == None:
            #             each_update_list[19] = ''
            #         if each_update_list[21] == None:
            #             each_update_list[21] = ''
            #         sql_string = 'update ' + GeneralParameters.recruit_table + " set r_status='" + each_update_list[0] + \
            #                      "',r_name='" + each_update_list[2] + "',r_sex='" + each_update_list[3] + \
            #                      "',r_Idcard='" + each_update_list[4] + "',r_contact='" + each_update_list[5] + \
            #                      "',r_interview=to_date('" + str(each_update_list[6]) + "','yyyy-mm-dd hh24:mi:ss')" + \
            #                      ",r_bureau='" + each_update_list[7] + \
            #                      "',r_department='" + each_update_list[8] + "',r_position='" + each_update_list[9] + \
            #                      "',r_demand01='" + each_update_list[10] + "',r_demand02='" + each_update_list[11] + \
            #                      "',r_source='" + each_update_list[12] + "',r_recruiter='" + each_update_list[13] + \
            #                      "',r_degree='" + each_update_list[14] + "',r_grade='" + each_update_list[15] + \
            #                      "',r_result01='" + each_update_list[16] + "',r_result02='" + each_update_list[17] + \
            #                      "',r_progress='" + each_update_list[18] + \
            #                      "',r_healthcheck=to_date('" + str(each_update_list[19]) + "','yyyy-mm-dd hh24:mi:ss')" + \
            #                      ",r_checkresult='" + each_update_list[20] + \
            #                      "',r_register=to_date('" + str(each_update_list[21]) + "','yyyy-mm-dd hh24:mi:ss')" + \
            #                      ",r_anomaly='" + each_update_list[22] + "' where r_number='" + each_update_list[1] + \
            #                      "' and r_Idcard='" + each_update_list[4] + "'"
            #         self.dml_obj.updateData(sql_string)
            self.writeTxt("insert Recruit招募进度", "刪除舊数据 与 加入新数据 完成")
        else:
            self.writeTxt("insert Recruit招募进度", "Excel文件中没有数据")
        self.writeTxt("insert Recruit招募进度", "Finished")
        logging.info("Finished insertRecruit!!")

    def insertCrd(self):
        self.file_object.write("\n ---------------------Crd 刷卡信息----------------------- \n")
        self.writeTxt("insert Crd刷卡信息", "Beginning")
        crd_path = self.getCrdPath(GeneralParameters.crd_xls)
        all_crd_file_list = os.listdir(crd_path)
        self.writeTxt("insert Crd刷卡信息", "Excel文件有'" + str(len(all_crd_file_list)) + "'个")
        for each_file_name in all_crd_file_list:
            each_xls_path = os.path.join(crd_path, each_file_name)
            if not each_xls_path:
                self.writeTxt("insert Crd刷卡信息", "没有 Excel文件")
                self.writeTxt("insert Crd刷卡信息", "Finished")
                continue

            crd_data = self.getCsvData(each_xls_path)
            if crd_data:
                crd_data = self.deleteCrdData(crd_data)
                crd_data = self.forDateField(crd_data, [3], "%Y/%m/%d")
                crd_data = self.forDateField(crd_data, [8, 10], "%Y/%m/%d %H:%M:%S")

                this_crd_eemployee_id = str(crd_data[0][2])
                this_crd_time = str(crd_data[0][3])
                if self.dml_obj.selectData("c_id", GeneralParameters.crd_table,
                                           "eemployee_id = '%s' and c_datetime =to_date('%s','yyyy-mm-dd hh24:mi:ss')" % (
                                                   this_crd_eemployee_id, this_crd_time)):
                    print " 已存在 该日期资料"
                    print "----- Finished insert crd_table!!"
                    self.writeTxt("insert Crd刷卡信息", "资料已存在，不需写入数据库")
                    continue

                self.insertExcept(crd_data, GeneralParameters.crd_order_string, GeneralParameters.crd_table,
                                  "insert Crd刷卡信息")
            else:
                self.writeTxt("insert Crd刷卡信息", "Excel文件中没有数据")
        logging.info("Finished insertCrd!!")
        self.writeTxt("insert Crd刷卡信息", "Finished")

    def insert_golden_stone_project(self):
        """插入 金石专案结案申请单 信息"""
        report_path = self.getXlsPath(GeneralParameters.report_xls)
        # print('report_path: ', report_path)
        if not report_path:
            print('no excel file')
            return
        # report_data = self.getXlsData(report_path)
        report_data = self.parse_html(report_path)
        title = report_data[0]
        need_col = [u'專案編號', u'部門', u'廠區', u'專案類別', u'專案名稱', u'表單狀態', u'簽核步驟', u'預估績效(月)',
                    u'提案人', u'提案人工號', u'實際完成日期', u'創建日期', u'課級信息', u'上一簽核步驟', u'簽核意見']
        # print('report_data title: ', title)
        index_list = []
        for i, col in enumerate(title):
            if col in need_col:
                if i not in index_list:
                    index_list.append(i)
        # print('index_list:', index_list)
        db_data = []
        for index, data in enumerate(report_data[1:]):
            each_need_row = []
            # select leader from eemployee where e_id = data[9]
            res = self.dml_obj.selectData("E_LEADER", GeneralParameters.employee_table, "E_ID = '" + data[24] + "'")
            # print('res:', res)
            if res:
                leader = res[0][0]
            else:
                # print('e_id:', data[24])
                leader = ''
            for i, each_row in enumerate(data):
                if i in index_list:
                    if i == 26 or i == 27:
                        data[i] = datetime.strptime(data[i], "%Y/%m/%d")
                    each_need_row.append(data[i])
            each_need_row.append(leader)
            db_data.append(each_need_row)
        # print('db_data')
        # 插入数据之前删除当年度数据
        self.dml_obj.deleteData(GeneralParameters.golden_stone_project_table,
                                "to_char(CREATE_TIME,'yyyy')= to_char(sysdate,'yyyy')")

        self.insertExcept(db_data, GeneralParameters.golden_stone_order_string,
                          GeneralParameters.golden_stone_project_table, "insert 金石结案申请单")
        logging.info("Finished insert golden_stone_project data!!")

    def parse_html(self, xls_path):
        soup = BeautifulSoup(OpenFile(xls_path).file_str)
        data = []
        for tr in soup.find_all('tr'):
            each_tr = []
            for td in tr.find_all('td'):
                if td.contents:
                    each_tr.append(td.contents[0])
                else:
                    each_tr.append(None)
            data.append(each_tr)
        return data

    def insert_egspbyleader(self):
        """根据golden_stone_project_table数据获取 每个leader每个function team有多少个金石专案"""
        # 金石专案结案数据 -- 计算 结案 已发起 数量(簽核中、已完成)
        # res = self.dml_obj.selectData('e_cname', GeneralParameters.employee_table, "e_id='F12332251'")
        # print(res) []
        # return
        teams = self.dml_obj.selectData('t_team, t_leader', GeneralParameters.team_table, 't_subject_leader is not null')

        gsp_data = self.dml_obj.selectData("E_LEADER, E_SPONSOR_ID, E_PERFORMANCE",
                                           GeneralParameters.golden_stone_project_table,
                                           "to_char(E_CREATE_DATE,'yyyy')= to_char(sysdate,'yyyy') and E_LEADER is not null and E_FORM_STATUS IN (u'已完成', u'簽核中')")
        # 金石专案立案数据 -- 计算 立案已完成数量
        register_data = self.dml_obj.selectData('E_LEADER, E_SPONSOR_ID', GeneralParameters.register_project_table,
                                                "to_char(E_CREATE_DATE,'yyyy')= to_char(sysdate,'yyyy') and E_LEADER is not null and E_FORM_STATUS= u'已完成'")
        team_dict_2 = {}
        for t in teams:
            team_dict_2[t[0]] = [t[1], 0]
            for r_data in register_data:
                _team = self.dml_obj.selectData("E_FUNCTIONTEAM", GeneralParameters.employee_table,
                                                "E_ID = '" + r_data[1] + "'")
                if t[0] == _team[0][0]:
                    team_dict_2[t[0]][1] += 1
        # team_list_2 = []
        # for r_data in register_data:
        #     # print(data)
        #     _team = self.dml_obj.selectData("E_FUNCTIONTEAM", GeneralParameters.employee_table,
        #                                     "E_ID = '" + r_data[1] + "'")
        #     if _team:
        #         team_list_2.append(_team[0][0])
        #
        # team_dict_2 = Counter(team_list_2)

        team_data = {}
        # for team, v in team_dict_2.items():
        #     # leader num_1, num_2, performance, target, hc
        #     team_data[team] = [v[0], v[1], 0, 0, 0, 0]
        #     for data in gsp_data:
        #         function_team = self.dml_obj.selectData("E_FUNCTIONTEAM", GeneralParameters.employee_table,
        #                                                 "E_ID = '" + data[1] + "'")
        #         if function_team:
        #
        #             pass
        for data in gsp_data:
            # print(data)
            function_team = self.dml_obj.selectData("E_FUNCTIONTEAM", GeneralParameters.employee_table,
                                                   "E_ID = '" + data[1] + "'")
            if function_team:
                team_name = function_team[0][0]
                # if team_name in team_dict_2.keys():
                #     leader = team_dict_2[team_name][0]
                #     # 立案已完成数量
                #     num_1 = team_dict_2[team_name][1]

                if team_name not in team_data.keys():
                    # 年初team人数
                    hc = self.get_team_hc(team_name)
                    # 年度目标专案数量 四舍五入
                    target = (hc/2) + (hc%2)
                    # 立案已完成数量
                    num_1 = team_dict_2[team_name][1] if team_name in team_dict_2.keys() else 0
                    # 结案已发起数量
                    num_2 = 1
                    performance = data[2]
                    leader_name = data[0]
                    team_data[team_name] = [leader_name, num_1, num_2, performance, target, hc]
                else:
                    # num_2 += 1
                    # performance += data[2]
                    team_data[team_name][2] += 1
                    team_data[team_name][3] += data[2]
        for k1 in team_dict_2.keys():
            if k1 not in team_data.keys():
                # team_data[k1] = []
                # team_data[k1].append(team_dict_2[k1][0])
                # team_data[k1].append(team_dict_2[k1][1])
                team_data[k1] = team_dict_2[k1]
                team_data[k1].append(0)
                team_data[k1].append(0)
                k1_hc = self.get_team_hc(k1)
                k1_target = (k1_hc/2) + (k1_hc % 2)
                # target
                team_data[k1].append(k1_target)
                # hc
                team_data[k1].append(k1_hc)

        db_data = []
        for k, v in team_data.items():
            each_team_data = []
            # function_team,leader, num_1, num_2, performance
            each_team_data.append(k)
            each_team_data.extend(v)
            # 结案 未发起数量
            num_3 = each_team_data[2]-each_team_data[3]
            each_team_data.insert(4, num_3)
            each_team_data[5] = each_team_data[5]/10
            each_team_data.append(str(time.localtime().tm_year))
            per_benefit = each_team_data[5]/each_team_data[7]
            each_team_data.append(per_benefit)
            db_data.append(each_team_data)
        # team_dict = Counter(function_team_list)
        # for k, v in team_dict.items():
        #     each_team_data = []
        #     leader_tup = self.dml_obj.selectData("T_LEADER", GeneralParameters.team_table, "T_TEAM = '" + k + "'")
        #     if leader_tup:
        #         leader = leader_tup[0][0]
        #         each_team_data.append(leader)
        #         each_team_data.append(k)
        #         each_team_data.append(v)
        #         each_team_data.append(str(time.localtime().tm_year))
        #         db_data.append(each_team_data)
        if db_data:
            # 插入数据之前删除当年度数据
            self.dml_obj.deleteData(GeneralParameters.gspbyleader_table, "e_year = to_char(sysdate,'yyyy')")
            self.insertExcept(db_data, GeneralParameters.gspbyleader_order_string, GeneralParameters.gspbyleader_table,
                              'insert gspbyleader_table')
        logging.info('insert gspbyleader_table data success')

    def get_team_hc(self, team_name):
        """获取每个team年初的人数 常设师级
        常设师级 --> 在职(入职日期小于 当年1月1日) + 离职(离场日期大于当年度1月1日)
        """
        # team_name = 'FATP Data'
        year_date = str(time.localtime().tm_year) + '-01-01 00:00:00'
        where_sql_1 = "e_functionteam='" + team_name + "' and e_status='" + u"在職" + "' and e_category = '"+ u"常設"+"' and" + \
                           " e_grade like '%" + u"師" + "%'" + \
                           " and e_firstdate < to_date('%s', 'yyyy-mm-dd hh24:mi:ss')" %(year_date)
        where_sql_2 = "e_functionteam='" + team_name + "' and e_status='" + u"離職" + "' and e_category = '"+ u"常設"+"' and" + \
                           " e_grade like '%" + u"師" + "%'" + \
                           " and e_lastdate > to_date('%s', 'yyyy-mm-dd hh24:mi:ss')" %(year_date)
        res_1 = self.dml_obj.selectData('e_id', GeneralParameters.employee_table, where_sql_1)
        res_2 = self.dml_obj.selectData('e_id', GeneralParameters.employee_table, where_sql_2)
        # print(res_1)
        # print(res_2)
        hc = len(res_1) + len(res_2)
        # print('hc:', hc)
        return hc

    def insert_register_project(self):
        """插入 金石专案立案申请表信息"""
        report_path = self.getXlsPath(GeneralParameters.report_xls)
        print(report_path)
        if not report_path:
            print('no excel file')
            return
        # report_data = self.getXlsData(report_path)
        report_data = self.parse_html(report_path)
        title = report_data[0]
        need_col = [u'專案編號', u'部門', u'廠區', u'專案類別', u'專案名稱', u'表單狀態', u'簽核步驟', u'預估績效',
                    u'提案人', u'提案人工號', u'預計完成日期', u'創建日期', u'課級信息', u'上一簽核步驟', u'簽核意見']
        print('report_data title: ', title)
        index_list = []
        for i, col in enumerate(title):
            if col in need_col:
                if i not in index_list:
                    index_list.append(i)
        print('index_list:', index_list)
        db_data = []
        for index, data in enumerate(report_data[1:]):
            each_need_row = []
            # select leader from eemployee where e_id = data[9]
            res = self.dml_obj.selectData("E_LEADER", GeneralParameters.employee_table, "E_ID = '" + data[21] + "'")
            # print('res:', res)
            if res:
                leader = res[0][0]
            else:
                # print('e_id:', data[24])
                leader = ''
            for i, each_row in enumerate(data):
                if i in index_list:
                    if i == 23 or i == 24:
                        data[i] = datetime.strptime(data[i], "%Y/%m/%d")
                    elif i == 14:
                        # print(repr(data[i]))
                        data[i] = float(data[i].replace(',', ''))
                    else:
                        data[i] = str(data[i])
                    each_need_row.append(data[i])
            each_need_row.append(leader)
            db_data.append(each_need_row)
        if db_data:
            # 插入数据之前删除当年度数据
            self.dml_obj.deleteData(GeneralParameters.register_project_table,
                                    "to_char(CREATE_TIME,'yyyy')= to_char(sysdate,'yyyy')")
            self.insertExcept(db_data, GeneralParameters.register_project_order_string,
                              GeneralParameters.register_project_table, "insert 金石立案申请单")
        logging.info(u'insert 金石立案申请单')

    def insert_etravel(self):
        xls_path = u'D:\OracleData\EERF\Travel\員工出差%26銷差狀況統計表_20191127.xls'
        html_str = OpenFile(xls_path).file_str
        soup = BeautifulSoup(html_str)
        origin_data = []
        title = []
        for i, tr in enumerate(soup.find_all('tr')):
            each_tr = []
            title_tr = []
            for j, th in enumerate(tr.find_all('th')):
                title_tr.append(th.contents[0])
            if title_tr:
                title.append(title_tr)
            for td in tr.find_all('td'):
                each_tr.append(td.contents[0])
            if each_tr:
                origin_data.append(each_tr)
        all_title = title[0][:5] + title[1]
        need_title = [u'工號', u'姓名', u'出差類型', u'出差單號', u'狀態', u'出差開始日期', u'出差結束日期', u'出差天數']
        need_index = []
        for index, t in enumerate(all_title):
            if t in need_title:
                if index not in need_index:
                    need_index.append(index)
            if len(need_index) == len(need_title):
                break
        db_data = []
        for k, data in enumerate(origin_data):
            each_row = []
            for l, col_data in enumerate(data):
                if l in need_index:
                    if l == 7 or l == 8:
                        # print('k:', k)
                        # print('col_data:', col_data)
                        if col_data.strip():
                            col_data = datetime.strptime(col_data, "%Y/%m/%d")
                        else:
                            col_data = None
                    if l == 9:
                        col_data = float(str(col_data))
                    each_row.append(col_data)
            leader_team_tup = self.dml_obj.selectData("E_FUNCTIONTEAM,E_LEADER", GeneralParameters.employee_table,
                                                      "E_ID = '" + data[1] + "'")
            if leader_team_tup:
                function_team = leader_team_tup[0][0]
                leader = leader_team_tup[0][1]
            each_row.append(function_team)
            each_row.append(leader)
            db_data.append(each_row)
        # 插入数据
        self.insertExcept(db_data, GeneralParameters.etravel_order_string, GeneralParameters.etravel_table,
                          "insert 国内外出差信息表")
        logging.info('insert 国内外出差信息表数据')

    def insert_travel_count(self):
        self.file_object.write("\n ---------------------TravelNum 出差次数----------------------- \n")
        self.writeTxt("insert TravelNum 出差次数", "Beginning")
        # domestic_data = self.dml_obj.selectData('ee_id, ee_name, e_travel_type, e_start_date, e_functionteam, e_leader',
        #                         GeneralParameters.etravel_table, "e_status='簽核完成' and e_travel_type='國內出差申請'")
        # foreign_data = self.dml_obj.selectData('ee_id, ee_name, e_travel_type, e_start_date, e_function_team, e_leader',
        #                         GeneralParameters.etravel_table, "e_status='簽核完成' and e_travel_type='國外出差申請'")
        self.dml_obj.deleteData(GeneralParameters.etravelcount_table,
                                "to_char(t_datetime,'yyyy')= to_char(sysdate,'yyyy')")
        domestic_data = self.arrange_travel_data(u'國內出差申請')
        foreign_data = self.arrange_travel_data(u'國外出差申請')
        self.insertExcept(domestic_data, GeneralParameters.etravelcount_order_string,
                          GeneralParameters.etravelcount_table, '国内出差申请次数')
        self.insertExcept(foreign_data, GeneralParameters.etravelcount_order_string,
                          GeneralParameters.etravelcount_table, '国外出差申请次数')
        logging.info('insert etravelcount_table data')

    def arrange_travel_data(self, type):
        """处理国内/国外出差数据
        返回 每个月 每个team 国内/国外 出差的次数
        """
        travel_data = self.dml_obj.selectData(
            'ee_id, ee_name, e_travel_type, e_start_date, e_functionteam, e_leader, e_travel_days',
            GeneralParameters.etravel_table,
            "e_status= u'簽核完成' and e_travel_type='" + type + "'")
        month_data_dict = {}
        for data in travel_data:
            date_tup = (data[3].year, data[3].month)
            if date_tup not in month_data_dict:
                month_data_dict[date_tup] = [data]
            else:
                month_data_dict[date_tup].append(data)

        db_data = []
        for k, v in month_data_dict.items():
            teams_data_dict = {}
            for d in v:
                if d[4] not in teams_data_dict:
                    teams_data_dict[d[4]] = d[6]
                else:
                    teams_data_dict[d[4]] += d[6]
            # teams_list = [x[4] for x in v]
            # team_dict = Counter(teams_list)
            for team, num in teams_data_dict.items():
                leader_tup = self.dml_obj.selectData("T_LEADER", GeneralParameters.team_table,
                                                     "T_TEAM = '" + team + "'")
                if leader_tup:
                    # leader, team, type, count, datetime
                    date_time = datetime.strptime(str(k[0]) + '-' + str(k[1]) + '-1', "%Y-%m-%d")
                    each_row_data = [leader_tup[0][0], team, type, num, date_time]
                    db_data.append(each_row_data)

        return db_data

    def insertDimission(self):
        """
        先清空当年数据，在进行数据插入
        :return:
        """
        self.file_object.write("\n ---------------------Dimission 离职----------------------- \n")
        self.writeTxt("insert Dimission离职", "Beginning")
        dimission_path = self.getXlsPath(GeneralParameters.leave_work_xls)
        if not dimission_path:
            self.writeTxt("insert Dimission离职", "没有 Excel文件")
            self.writeTxt("insert Dimission离职", "Finished")
            return
        # TODO:删除当年离职数据
        # 刪除當年插入的所有數據
        self.dml_obj.deleteData(GeneralParameters.leave_work_table,
                                "to_char(CREATE_TIME,'yyyy')= to_char(sysdate,'yyyy')")
        dimission_data = self.getXlsData(dimission_path)
        if dimission_data:
            dimission_data = self.getDimissionData(dimission_data, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16])
            # self.printData(dimission_data)
            dimission_data = self.forDateField(dimission_data[1:], [9], "%Y-%m-%d")
            dimission_data = self.forDateField(dimission_data, [11, 12], "%Y/%m/%d")
            # 判断是否 该单号是需要 insert_recruit_data 还是 update_recruit_data
            insert_dimission_data, update_dimission_data = self.getInsertData("d_number",
                                                                              GeneralParameters.leave_work_table,
                                                                              dimission_data, 1)

            # 新資料和已存在的資料統一合併成insert_dimission_data，重新寫入數據庫
            insert_dimission_data = insert_dimission_data + update_dimission_data
            # Insert dismission data to DB
            if insert_dimission_data:
                self.insertExcept(insert_dimission_data, GeneralParameters.leave_work_order_string,
                                  GeneralParameters.leave_work_table, "insert Dimission离职")
                logging.info("Finished insert_dimission_data!!")

            # Disable update function
            # for each_update_list in update_dimission_data:
            #     if each_update_list:
            #         if each_update_list[9] == None:
            #             each_update_list[9] = ""
            #         if each_update_list[11] == None:
            #             each_update_list[11] = ""
            #         if each_update_list[12] == None:
            #             each_update_list[12] = ""
            #         sql_string = 'update ' + GeneralParameters.leave_work_table + " set d_step='" + each_update_list[
            #             0] + \
            #                      "',d_cname='" + each_update_list[2] + "',d_department='" + each_update_list[3] + \
            #                      "',d_grade='" + each_update_list[4] + "',d_management='" + each_update_list[5] + \
            #                      "',d_reason01='" + each_update_list[6] + "',d_reason02='" + each_update_list[7] + \
            #                      "',d_reason03='" + each_update_list[8] + \
            #                      "',d_firstdate=to_date('" + str(each_update_list[9]) + "','yyyy-mm-dd hh24:mi:ss')" + \
            #                      ",d_seniority='" + each_update_list[10] + \
            #                      "',d_lastdate=to_date('" + str(each_update_list[11]) + "','yyyy-mm-dd hh24:mi:ss')" + \
            #                      ",d_requestdate=to_date('" + str(each_update_list[12]) + "','yyyy-mm-dd hh24:mi:ss')" + \
            #                      " where d_number='" + each_update_list[1] + "'"
            #         self.dml_obj.updateData(sql_string)
            self.writeTxt("insert Dimission离职", "插入数据 完成")
        else:
            self.writeTxt("insert Dimission离职", "Excel文件中没有数据")
        self.writeTxt("insert Dimission离职", "Finished")
        logging.info("Finished insertDimission!!")

    def insertattendanceanomaly(self):
        """
        陆干 先清空當月數據，再插入最新數據
        :return:
        """
        self.file_object.write("\n ---------------------Attendanceanomaly 考勤異常----------------------- \n")
        self.writeTxt("insert Attendanceanomaly考勤異常", "Beginning")
        attendanceanomaly_path_1 = self.setXlsPath(GeneralParameters.attendanceanomaly_xls[0])
        attendanceanomaly_path_2 = self.setXlsPath(GeneralParameters.attendanceanomaly_xls[1])
        attendanceanomaly_data = []
        if not attendanceanomaly_path_1:
            self.writeTxt("insert Attendanceanomaly考勤異常", "没有 Excel 1文件")

        else:
            attendanceanomaly_data_1 = self.getCsvData(attendanceanomaly_path_1)
            if attendanceanomaly_data_1:
                attendanceanomaly_data.extend(attendanceanomaly_data_1[1:])
        if not attendanceanomaly_path_2:
            self.writeTxt("insert Attendanceanomaly考勤異常", "没有 Excel 2文件")

        else:
            attendanceanomaly_data_2 = self.getCsvData(attendanceanomaly_path_2)
            if attendanceanomaly_data_2:
                attendanceanomaly_data.extend(attendanceanomaly_data_2[1:])
        if attendanceanomaly_data:
            self.dml_obj.deleteData(GeneralParameters.attendanceanomaly_table, "A_ID > 0")
            attendanceanomaly_data = self.forDateField(attendanceanomaly_data, [12, 17], "%Y/%m/%d %H:%M:%S")
            attendanceanomaly_data = self.forDateField(attendanceanomaly_data, [7], "%Y/%m/%d")
            attendanceanomaly_data_2 = []
            for i in attendanceanomaly_data:
                try:
                    if i[14]:
                        i[14] = float(i[14])
                    else:
                        i[14] = None
                    if i[19]:
                        i[19] = float(i[19])
                    else:
                        i[19] = None
                    try:
                        i[4] = self.dml_obj.selectData("E_FUNCTIONTEAM", GeneralParameters.employee_table,
                                                       "E_ID = '" + i[5] + "'")[0][0]
                    except Exception as e:
                        self.writeTxt("insert ATTENDANCEANOMALY考勤異常信息 error:", e)
                    if "?" in i[6]:
                        try:
                            if self.dml_obj.selectData("E_CNAME", GeneralParameters.employee_table,
                                                       "E_ID = '" + i[5] + "'"):
                                i[6] = self.dml_obj.selectData("E_CNAME", GeneralParameters.employee_table,
                                                               "E_ID = '" + i[5] + "'")[0][0]
                            else:
                                i[6] = i[6].replace("?", "x")
                        except Exception as e:
                            self.writeTxt("insert ATTENDANCEANOMALY考勤異常信息 error:", e)
                    attendanceanomaly_data_2.append(i[0: -1])
                except Exception as e:
                    logging.info(e)
                    continue
            # this_month_str = str(attendanceanomaly_data_2[0][7].year) +'-'+ str(attendanceanomaly_data_2[0][7].month) + '-01'
            # if attendanceanomaly_data_2[0][7].month == 12:
            #     next_month_str = str(attendanceanomaly_data_2[0][7].year + 1) +'-'+ '01' + '-01'
            # else:
            #     next_month_str = str(attendanceanomaly_data_2[0][7].year) + '-' + str(attendanceanomaly_data_2[0][7].month + 1) + '-01'
            # self.dml_obj.deleteData(GeneralParameters.attendanceanomaly_table,"A_DATETIME >= to_date('"+ this_month_str +"','yyyy-mm-dd') and A_DATETIME < to_date('"+ next_month_str +"','yyyy-mm-dd')")
            self.insertExcept(attendanceanomaly_data_2, GeneralParameters.eattendanceanomaly_order_string,
                              GeneralParameters.attendanceanomaly_table,
                              "insert ATTENDANCEANOMALY考勤異常信息")
        else:
            self.writeTxt("insert ATTENDANCEANOMALY考勤異常信息", "Excel文件中没有数据")

        logging.info("Finished insertattendanceanomaly!!")
        self.writeTxt("insert ATTENDANCEANOMALY考勤異常信息", "Finished")

    def insertpzmsattendanceanomaly(self):
        """
        台干 插入最新數據
        :return:
        """
        self.file_object.write("\n ---------------------PZMSAttendanceanomaly 考勤異常----------------------- \n")
        self.writeTxt("insert PZMSAttendanceanomaly考勤異常", "Beginning")
        attendanceanomaly_path_1 = self.setXlsPath(GeneralParameters.pzmsattendanceanomaly_xls[0])
        attendanceanomaly_path_2 = self.setXlsPath(GeneralParameters.pzmsattendanceanomaly_xls[1])
        attendanceanomaly_data = []
        if not attendanceanomaly_path_1:
            self.writeTxt("insert PZMSAttendanceanomaly考勤異常", "没有 Excel 1文件")

        else:
            attendanceanomaly_data_1 = self.getXlsData(attendanceanomaly_path_1)
            if attendanceanomaly_data_1:
                attendanceanomaly_data.extend(attendanceanomaly_data_1[1:])
        if not attendanceanomaly_path_2:
            self.writeTxt("insert PZMSAttendanceanomaly考勤異常", "没有 Excel 2文件")

        else:
            attendanceanomaly_data_2 = self.getXlsData(attendanceanomaly_path_2)
            if attendanceanomaly_data_2:
                attendanceanomaly_data.extend(attendanceanomaly_data_2[1:])

        if attendanceanomaly_data:
            attendanceanomaly_data = self.forDateField(attendanceanomaly_data, [11, 16], "%Y/%m/%d %H:%M:%S")
            attendanceanomaly_data = self.forDateField(attendanceanomaly_data, [5], "%Y/%m/%d")
            attendanceanomaly_data_2 = []
            for i in attendanceanomaly_data:
                if i[13] and i[13] != " ":
                    i[13] = float(i[13])
                else:
                    i[13] = None
                if i[18] and i[18] != " ":
                    i[18] = float(i[18])
                else:
                    i[18] = None
                try:
                    i[1] = self.dml_obj.selectData("E_FUNCTIONTEAM", GeneralParameters.employee_table,
                                                   "E_ID = '" + i[2] + "'")[0][0]
                except Exception as e:
                    self.writeTxt("insert PZMSAttendanceanomaly考勤異常 error:", e)
                if "?" in i[3]:
                    try:
                        i[3] = self.dml_obj.selectData("E_CNAME", GeneralParameters.employee_table,
                                                       "E_ID = '" + i[2] + "'")[0][0]
                    except Exception as e:
                        self.writeTxt("insert PZMSAttendanceanomaly考勤異常 error:", e)

                i_order = [u"", i[9], u'iDPBG 新產品工程 EERF處', u"", i[1], i[2], i[3], i[5], i[6], i[7], i[8], i[10], i[11],
                           i[12], i[13], i[14], i[15], i[16], i[17], i[18], i[19]]
                attendanceanomaly_data_2.append(i_order[0:])
            # this_month_str = str(attendanceanomaly_data_2[0][7].year) +'-'+ str(attendanceanomaly_data_2[0][7].month) + '-01'
            # if attendanceanomaly_data_2[0][7].month == 12:
            #     next_month_str = str(attendanceanomaly_data_2[0][7].year + 1) +'-'+ '01' + '-01'
            # else:
            #     next_month_str = str(attendanceanomaly_data_2[0][7].year) + '-' + str(attendanceanomaly_data_2[0][7].month + 1) + '-01'
            # self.dml_obj.deleteData(GeneralParameters.attendanceanomaly_table,"A_DATETIME >= to_date('"+ this_month_str +"','yyyy-mm-dd') and A_DATETIME < to_date('"+ next_month_str +"','yyyy-mm-dd')")
            self.insertExcept(attendanceanomaly_data_2, GeneralParameters.eattendanceanomaly_order_string,
                              GeneralParameters.attendanceanomaly_table,
                              "insert PZMSAttendanceanomaly考勤異常")
        else:
            self.writeTxt("insert PZMSAttendanceanomaly考勤異常", "Excel文件中没有数据")

        logging.info("Finished insertpzmsattendanceanomaly!!")
        self.writeTxt("insert PZMSAttendanceanomaly考勤異常", "Finished")

    def insert_attendance_history(self):
        """
            每天插入最新數據
        :return:
        """
        self.file_object.write("\n ---------------------Insert_attendance_history 考勤異常历史----------------------- \n")
        self.writeTxt("insert Insert_attendance_history 考勤異常历史", "Beginning")
        attendanceanomaly_path_1 = self.setXlsPath(GeneralParameters.attendanceanomaly_xls[0])
        attendanceanomaly_path_2 = self.setXlsPath(GeneralParameters.attendanceanomaly_xls[1])
        attendanceanomaly_data = []
        # 当前时间
        today = datetime.now()
        # 测试
        # today = datetime.strptime("2019-10-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        # 当前月1号
        month_first = today.replace(day=1)

        if not attendanceanomaly_path_1:
            self.writeTxt("insert Insert_attendance_history 考勤異常历史", "没有 Excel 1文件")

        else:
            attendanceanomaly_data_1 = self.getCsvData(attendanceanomaly_path_1)
            if attendanceanomaly_data_1:
                attendanceanomaly_data.extend(attendanceanomaly_data_1[1:])
        if not attendanceanomaly_path_2:
            self.writeTxt("insert Attendance_history 考勤異常历史", "没有 Excel 2文件")

        else:
            # 出现Excel 2文件 那就删除上个月数据
            attendanceanomaly_data_2 = self.getCsvData(attendanceanomaly_path_2)
            if attendanceanomaly_data_2:
                attendanceanomaly_data.extend(attendanceanomaly_data_2[1:])
            # 上个月月末
            last_month_end = month_first - timedelta(days=1)
            # 上个月1号
            last_month_first = last_month_end.replace(day=1)

            last_month_end_time = str(last_month_end).split(" ")[0]
            last_month_start_time = str(last_month_first).split(" ")[0]
            # 删除上个月数据
            self.dml_obj.deleteData(GeneralParameters.attendancehistory_table,
                                    "a_datetime between to_date('%s 00:00:00', 'yyyy-mm-dd hh24:mi:ss') and to_date('%s 00:00:00', 'yyyy-mm-dd hh24:mi:ss')" % (
                                        last_month_start_time, last_month_end_time))

        if attendanceanomaly_data:
            # 删除当前月
            start_time = str(month_first).split(" ")[0]
            # 获取当月天数 monthRange
            wday, monthRange = calendar.monthrange(today.year, today.month)
            end_time = '%d-%02d-%02d' % (today.year, today.month, monthRange)
            # 删除当前月
            self.dml_obj.deleteData(GeneralParameters.attendancehistory_table,
                                    "a_datetime between to_date('%s 00:00:00', 'yyyy-mm-dd hh24:mi:ss') and to_date('%s 00:00:00', 'yyyy-mm-dd hh24:mi:ss')" % (
                                        start_time, end_time))
            attendanceanomaly_data = self.forDateField(attendanceanomaly_data, [12, 17], "%Y/%m/%d %H:%M:%S")
            attendanceanomaly_data = self.forDateField(attendanceanomaly_data, [7], "%Y/%m/%d")
            attendanceanomaly_data_2 = []
            for i in attendanceanomaly_data:
                if i[14]:
                    i[14] = float(i[14])
                else:
                    i[14] = None
                if i[19]:
                    i[19] = float(i[19])
                else:
                    i[19] = None
                try:
                    i[4] = self.dml_obj.selectData("E_FUNCTIONTEAM", GeneralParameters.employee_table,
                                                   "E_ID = '" + i[5] + "'")[0][0]
                except Exception as e:
                    self.writeTxt("insert Attendance_history 考勤異常历史 error:", e)
                if "?" in i[6]:
                    try:
                        i[6] = self.dml_obj.selectData("E_CNAME", GeneralParameters.employee_table,
                                                       "E_ID = '" + i[5] + "'")[0][0]
                    except Exception as e:
                        self.writeTxt("insert Attendance_history 考勤異常历史 error:", e)
                attendanceanomaly_data_2.append(i[0: -1])
            # this_month_str = str(attendanceanomaly_data_2[0][7].year) +'-'+ str(attendanceanomaly_data_2[0][7].month) + '-01'
            # if attendanceanomaly_data_2[0][7].month == 12:
            #     next_month_str = str(attendanceanomaly_data_2[0][7].year + 1) +'-'+ '01' + '-01'
            # else:
            #     next_month_str = str(attendanceanomaly_data_2[0][7].year) + '-' + str(attendanceanomaly_data_2[0][7].month + 1) + '-01'
            # self.dml_obj.deleteData(GeneralParameters.attendanceanomaly_table,"A_DATETIME >= to_date('"+ this_month_str +"','yyyy-mm-dd') and A_DATETIME < to_date('"+ next_month_str +"','yyyy-mm-dd')")
            self.insertExcept(attendanceanomaly_data_2, GeneralParameters.eattendanceanomaly_order_string,
                              GeneralParameters.attendancehistory_table,
                              "insert Attendance_history 考勤異常历史")
        else:
            self.writeTxt("insert Attendance_history 考勤異常历史", "Excel文件中没有数据")

        logging.info("Finished Attendance_history!!")
        self.writeTxt("insert Attendance_history 考勤異常历史", "Finished")

    def insert_PZMS_attendance_history(self):
        """
            台干 考勤异常每天插入最新數據
        :return:
        """
        self.file_object.write(
            "\n ---------------------insert_PZMS_attendance_history 台干考勤異常历史----------------------- \n")
        self.writeTxt("insert insert_PZMS_attendance_history 台干考勤異常历史", "Beginning")
        attendanceanomaly_path_1 = self.setXlsPath(GeneralParameters.pzmsattendanceanomaly_xls[0])
        attendanceanomaly_path_2 = self.setXlsPath(GeneralParameters.pzmsattendanceanomaly_xls[1])
        attendanceanomaly_data = []
        # 当前时间
        today = datetime.now()
        # 测试
        # today = datetime.strptime("2019-10-01 00:00:00", "%Y-%m-%d %H:%M:%S")

        if not attendanceanomaly_path_1:
            self.writeTxt("insert insert_PZMS_attendance_history 台干考勤異常历史", "没有 Excel 1文件")

        else:
            attendanceanomaly_data_1 = self.getXlsData(attendanceanomaly_path_1)
            if attendanceanomaly_data_1:
                attendanceanomaly_data.extend(attendanceanomaly_data_1[1:])
        if not attendanceanomaly_path_2:
            self.writeTxt("insert PZMS Attendance_history 台干考勤異常历史", "没有 Excel 2文件")

        else:
            # 出现Excel 2文件 那就删除上个月数据
            attendanceanomaly_data_2 = self.getXlsData(attendanceanomaly_path_2)
            if attendanceanomaly_data_2:
                attendanceanomaly_data.extend(attendanceanomaly_data_2[1:])

        if attendanceanomaly_data:
            attendanceanomaly_data = self.forDateField(attendanceanomaly_data, [11, 16], "%Y/%m/%d %H:%M:%S")
            attendanceanomaly_data = self.forDateField(attendanceanomaly_data, [5], "%Y/%m/%d")
            attendanceanomaly_data_2 = []
            for i in attendanceanomaly_data:
                if i[13] and i[13] != " ":
                    i[13] = float(i[13])
                else:
                    i[13] = None
                if i[18] and i[18] != " ":
                    i[18] = float(i[18])
                else:
                    i[18] = None
                try:
                    i[1] = self.dml_obj.selectData("E_FUNCTIONTEAM", GeneralParameters.employee_table,
                                                   "E_ID = '" + i[2] + "'")[0][0]
                except Exception as e:
                    self.writeTxt("insert PZMS_attendance_history 台干考勤異常历史 error:", e)
                if "?" in i[3]:
                    try:
                        i[3] = self.dml_obj.selectData("E_CNAME", GeneralParameters.employee_table,
                                                       "E_ID = '" + i[2] + "'")[0][0]
                    except Exception as e:
                        self.writeTxt("insert PZMSAttendanceanomaly台干考勤異常历史 error:", e)

                i_order = [u"", i[9], u'iDPBG 新產品工程 EERF處', u"", i[1], i[2], i[3], i[5], i[6], i[7], i[8], i[10], i[11],
                           i[12], i[13], i[14], i[15], i[16], i[17], i[18], i[19]]
                attendanceanomaly_data_2.append(i_order[0:])
            # this_month_str = str(attendanceanomaly_data_2[0][7].year) +'-'+ str(attendanceanomaly_data_2[0][7].month) + '-01'
            # if attendanceanomaly_data_2[0][7].month == 12:
            #     next_month_str = str(attendanceanomaly_data_2[0][7].year + 1) +'-'+ '01' + '-01'
            # else:
            #     next_month_str = str(attendanceanomaly_data_2[0][7].year) + '-' + str(attendanceanomaly_data_2[0][7].month + 1) + '-01'
            # self.dml_obj.deleteData(GeneralParameters.attendanceanomaly_table,"A_DATETIME >= to_date('"+ this_month_str +"','yyyy-mm-dd') and A_DATETIME < to_date('"+ next_month_str +"','yyyy-mm-dd')")
            self.insertExcept(attendanceanomaly_data_2, GeneralParameters.eattendanceanomaly_order_string,
                              GeneralParameters.attendancehistory_table,
                              "insert PZMS Attendance_history 台干考勤異常历史")
        else:
            self.writeTxt("insert PZMS Attendance_history 台干考勤異常历史", "Excel文件中没有数据")

        logging.info("Finished PZMS Attendance_history!!")
        self.writeTxt("insert PZMS  Attendance_history 台干考勤異常历史", "Finished")

    def insertfalseattendance(self):
        self.file_object.write("\n ---------------------EFALSEATTENDANCE 虛報考勤----------------------- \n")
        self.writeTxt("insert EFALSEATTENDANCE 虛報考勤", "Beginning")
        falseattendance_path_1 = self.setXlsPath(GeneralParameters.falseattendance_xls[0])
        falseattendance_path_2 = self.setXlsPath(GeneralParameters.falseattendance_xls[1])
        falseattendance_data = []
        if not falseattendance_path_1:
            self.writeTxt("insert EFALSEATTENDANCE 虛報考勤", "没有 Excel 1文件")
        else:
            falseattendance_data_1 = self.getCsvData(falseattendance_path_1)
            if falseattendance_data_1:
                falseattendance_data.append(falseattendance_data_1)
            else:
                self.writeTxt("insert EFALSEATTENDANCE 虛報考勤", "Excel 1 文件中没有数据")
                self.writeTxt("insert EFALSEATTENDANCE 虛報考勤", "Finished")
                logging.info("Finished insertfalseattendance!!")
                return
        if not falseattendance_path_2:
            self.writeTxt("insert EFALSEATTENDANCE 虛報考勤", "没有 Excel 2文件")
        else:
            falseattendance_data_2 = self.getCsvData(falseattendance_path_2)
            if falseattendance_data_2:
                falseattendance_data.append(falseattendance_data_2)
            else:
                self.writeTxt("insert EFALSEATTENDANCE 虛報考勤", "第二個Excel文件中没有数据")
        falseattendance_insert_data = []
        for data in falseattendance_data:
            data = self.forDateField(data[1:], [8], "%Y/%m/%d")
            for i in data:
                i[10] = float(i[10])
                i = i[0:11]
                i[4] = \
                    self.dml_obj.selectData("E_FUNCTIONTEAM", GeneralParameters.employee_table,
                                            "E_ID = '" + i[5] + "'")[0][
                        0]
                falseattendance_insert_data.append(i)
        self.dml_obj.deleteData(GeneralParameters.falseattendacne_table,
                                "F_ID > 0")

        if falseattendance_insert_data:
            self.insertExcept(falseattendance_insert_data, GeneralParameters.efalseattendance_order_string,
                              GeneralParameters.falseattendacne_table,
                              "insert EFALSEATTENDANCE 虛報考勤")

        logging.info("Finished insertfalseattendance!!")
        self.writeTxt("insert EFALSEATTENDANCE 虛報考勤", "Finished")

    def insertemail(self):
        """
        存在的邮箱正确不更新, 系统更改正确的邮箱更新, 有新增的插入最新數據
        :return:
        """
        self.file_object.write("\n ---------------------EEAMIL 員工郵箱信息----------------------- \n")
        self.writeTxt("insert EEAMIL 員工郵箱信息", "Beginning")
        email_path = self.getXlsPath(GeneralParameters.email_xls)
        if not email_path:
            self.writeTxt("insert EEAMIL 員工郵箱信息", "没有 Excel文件")
            self.writeTxt("insert EEAMIL 員工郵箱信息", "Finish")
            return
        email_data = (self.getXlsData(email_path))[1:]
        if email_data:
            email_data_2 = []
            for i in email_data:
                personal_obj = self.dml_obj.selectData("*", GeneralParameters.email_table,
                                                       "E_EMPLOYEE = '" + i[6] + "'")
                name = i[7]
                emp_id = i[6]
                email = i[36]
                email_list = email.split('@')

                # 存在,接着判断邮件是否相同
                if personal_obj:
                    if email.encode('utf-8') != personal_obj[0][3]:
                        # 如果邮件为空或者格式错误都跳过
                        if email == '' or len(email_list) < 2:
                            continue
                        elif email_list[1] != 'foxconn.com' and email_list[1] != 'mail.foxconn.com':
                            continue
                        else:
                            # 不等于更新
                            sql_string = "update EEMAIL set E_EMAIL='%s' where E_EMPLOYEE = '%s'" % (
                                email, personal_obj[0][2])
                            self.dml_obj.updateData(sql_string)
                else:
                    #  数据库不存在---新增
                    if len(email_list) < 2:
                        email = ''
                    elif email_list[1] != 'foxconn.com' and email_list[1] != 'mail.foxconn.com':
                        email = ''
                    if email == '':
                        team = None
                        try:
                            team = self.dml_obj.selectData("E_FUNCTIONTEAM", GeneralParameters.employee_table,
                                                           "E_ID = '" + emp_id + "'")[0][0]
                        except Exception as e:
                            self.writeTxt("insert EEAMIL 員工郵箱信息 error:", (str(e) + "  " + str(emp_id)))
                        if team:
                            try:
                                email = self.dml_obj.selectData("T_ASSISTANTEMAIL", GeneralParameters.team_table,
                                                                "T_TEAM = '" + team + "'")[0][0]
                            except Exception as e:
                                self.writeTxt("insert EEAMIL 員工郵箱信息 error:", (str(e) + "  " + str(emp_id)))
                    email_data_2.append([name, emp_id, email])

            if email_data_2:
                self.insertExcept(email_data_2, GeneralParameters.eemail_order_string, GeneralParameters.email_table,
                                  "insert insert EEAMIL 員工郵箱信息")
        else:
            self.writeTxt("insert EEAMIL 員工郵箱信息", "Excel文件中没有数据")

        logging.info("Finished insertemail!!")
        self.writeTxt("insert EEAMIL 員工郵箱信息", "Finished")

    def insertOverhours(self):
        """
        @note: 员工提报加班时数汇总数据，写入数据库
        """
        # 获取 员工有效加班 数据
        over_hours_path = self.getXlsPath(GeneralParameters.over_hours_xls)
        if not over_hours_path:
            logging.info("End insertOverHours: not over_hours_path")
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
                self.dml_obj.insertData(insert_over_hours_data, GeneralParameters.over_hours_order_string_31,
                                        GeneralParameters.over_hours_table)
            elif this_xls_time_len == 30:
                self.dml_obj.insertData(insert_over_hours_data, GeneralParameters.over_hours_order_string_30,
                                        GeneralParameters.over_hours_table)
            elif this_xls_time_len == 29:
                self.dml_obj.insertData(insert_over_hours_data, GeneralParameters.over_hours_order_string_29,
                                        GeneralParameters.over_hours_table)
            else:
                self.dml_obj.insertData(insert_over_hours_data, GeneralParameters.over_hours_order_string_28,
                                        GeneralParameters.over_hours_table)
            logging.info("End insertOverHours!!")
        logging.info("End insertOverHours: insert_over_hours_data is null")

    def getCsvData(self, csv_path):
        csv_reader = csv.reader(open(csv_path, 'r'))
        csv_data = []
        for line in csv_reader:
            if not line:
                continue
            line_data = []
            for s_l in line:
                line_data.append(s_l.decode('big5hkscs'))

            csv_data.append(line_data)
        return csv_data

    def getDimissionData(self, data_list, index_list):
        dimission_data = []
        number_list = []
        for row_list in data_list:
            # Get employee ID, if already exist add in number_list, if exist don't add
            if row_list[3] in number_list:
                continue
            number_list.append(row_list[3])
            d_row_data = []
            for i in index_list:
                if i == 16:
                    d_row_data.append(row_list[i].split(' ')[0])
                else:
                    d_row_data.append(row_list[i])
                #             if not row_list[12] or row_list[12].isspace():
                #                 d_row_data.append(u'否')
                #             else:
                #                 d_row_data.append(u'是')

            dimission_data.append(d_row_data)

        return dimission_data

    def getPzmsData(self, data_list):

        index_list = [2, 4, 5, 6, 7, 8, 10, 11, 12, 13]
        pzms_list = []
        for row_list in data_list:
            pams_row = []
            for index_i in index_list:
                pams_row.append(row_list[index_i])
            pzms_list.append(pams_row)

        return pzms_list

    def deleteCrdData(self, data_list):
        """
        @note: 1.得到需要资料栏的位置 (crd_need_position);2.根据 crd_need_position 来获取数据
        """
        crd_title = data_list[0]
        crd_need_title = GeneralParameters.crd_need_title
        crd_need_position = []
        for col, each_title in enumerate(crd_title):
            for each_col in crd_need_title:
                if each_col == each_title and col not in crd_need_position:
                    crd_need_position.append(col)

        data = []
        for row_list in data_list:
            each_row = []
            for each_position in crd_need_position:
                each_row.append(row_list[each_position])
            if each_row:
                employee_id = each_row[2]
                if self.dml_obj.selectData("e_id", GeneralParameters.employee_table, "e_id = '%s'" % employee_id):
                    data.append(each_row)

        return data

    def getXlsPath(self, data_xls):
        try:
            xls_path = ''
            this_path = data_xls[0]
            dir_list = os.listdir(this_path)
            newDir = self.getNewDir(dir_list)
            # newDir = '2019-08-05-23-30-01'  # 测试专用
            date_dir_path = os.path.join(this_path, newDir)
            file_name = os.listdir(date_dir_path)[0]

            xls_path = os.path.join(date_dir_path, file_name)

        except:
            logging.info("No Excel file!!!!!!")
        return xls_path

    def setXlsPath(self, data_xls):
        try:
            xls_path = ''
            this_path = data_xls[0]
            dir_list = os.listdir(this_path)
            newDir = self.getNewDir(dir_list)
            # newDir = '2019-08-05-23-30-01'  # 测试专用
            date_dir_path = os.path.join(this_path, newDir)
            file_name = data_xls[1]
            for i in os.listdir(date_dir_path):
                if i == file_name:
                    xls_path = os.path.join(date_dir_path, file_name)
                    break



        except:
            logging.info("No Excel file!!!!!!")
        return xls_path

    def getCrdPath(self, data_xls):
        try:
            date_dir_path = ''
            this_path = data_xls[0]
            dir_list = os.listdir(this_path)
            newDir = self.getNewDir(dir_list)
            # newDir = '2019-03-15-23-00-03'
            date_dir_path = os.path.join(this_path, newDir)
        except:
            logging.info("Path Error!!!!!!")

        return date_dir_path

    def getFHRPath(self, data_xls):
        xls_path = ''
        print "getFHRPath data_xls[0]:", data_xls[0]
        this_path = data_xls[0]
        dir_list = os.listdir(this_path)
        newDir = self.getNewDir(dir_list)
        print "newDir:", newDir
        #         newDir = '2018-03-14-23-00-01'
        date_dir_path = os.path.join(this_path, newDir)
        print "date_dir_path:", date_dir_path

        for file_name in os.listdir(date_dir_path):
            #             print file_name.decode('big5'),type(file_name.decode('big5'))
            #             print data_xls[1],type(data_xls[1])
            if data_xls[1] in file_name.decode('big5'):
                xls_path = os.path.join(date_dir_path, file_name)
                print "xls_path:", xls_path
                return xls_path

        return xls_path

    def getFHRData(self, FHRpath):
        '''
        @note: 
        '''
        try:
            ## new
            _wb = xlrd.open_workbook(FHRpath)
            data = []
            for ws in _wb.sheets():
                rows = ws.nrows
                for i in range(0, rows):
                    row_data = ws.row_values(i)
                    data.append(row_data[:25])
        except:
            data = self.getXlsData(FHRpath)  ## old

        return data

    def forPzmsDateField(self, data_list, index_list, date_format):
        for row_list in data_list:
            for i in index_list:
                if not row_list[i] or row_list[i].isspace():
                    row_list[i] = None
                    continue
                if row_list[4] != u'晚班':
                    row_list[i] = datetime.strptime(datetime.strftime(row_list[1], "%Y/%m/%d") + ' ' + row_list[i],
                                                    date_format)
                else:
                    lastDate = row_list[1] + timedelta(days=1)
                    lastDate_str = datetime.strftime(lastDate, "%Y/%m/%d")
                    row_list[i] = datetime.strptime(lastDate_str + ' ' + row_list[i], date_format)

        return data_list

    def forDateField(self, data_list, index_list, date_format):
        for row_list in data_list:
            for i in index_list:
                if not row_list[i] or row_list[i].isspace():
                    row_list[i] = None
                    continue
                try:
                    row_list[i] = datetime.strptime(row_list[i], date_format)
                except:
                    try:
                        row_list[i] = datetime.strptime(row_list[i], "%Y/%m/%d %H:%M")
                    except:
                        continue
        return data_list

    def forSubjectField(self, data_list, index_list):
        '''
        @note: 
        '''
        new_subject_list = u'iDPBG EERF  EMC/RSE課_觀瀾'
        for row_data in data_list:
            for _index in index_list:
                if row_data[_index] == u'iDPBG EERF  EMC&RSE課_觀瀾' or row_data[_index] == u'iDPBG EERF  EMCEMC/RSE課_觀瀾':
                    row_data[_index] = new_subject_list
        return data_list

    def getXlsData(self, xls_path):
        '''
        @note: 引用 Sara 写的 API读取带有'<table><td>...'的excle文件，得到二维数组
        '''
        _obj = ExportTableData(xls_path)
        all_list = _obj.table_data
        return all_list

    def getXlsDate(self, data):
        '''
        @note: 获取该 excle 的年月
        '''
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

    def getNewDir(self, dir_list):
        n = len(dir_list)
        new_dir = dir_list[0]
        for r in range(n):
            if datetime.strptime(dir_list[r], "%Y-%m-%d-%H-%M-%S") > datetime.strptime(new_dir, "%Y-%m-%d-%H-%M-%S"):
                new_dir = dir_list[r]
        return new_dir

    def getSeniority(self, man_number):
        '''
        @note: 计算 年资
        '''
        this_firstdate_tup = self.dml_obj.selectData("e_firstdate", GeneralParameters.employee_table,
                                                     "e_id='%s'" % man_number)
        if this_firstdate_tup:
            this_firstdate_val = str(this_firstdate_tup[0][0])
            if this_firstdate_val == 'None':
                return ""
        else:
            return ""
        this_seniority_num = time.mktime(time.strptime(this_firstdate_val, '%Y-%m-%d %H:%M:%S'))
        now_time_num = time.mktime(time.localtime())
        this_seniority_val = str((now_time_num - this_seniority_num) / (60 * 60 * 24 * 365))
        this_seniority_val = float(this_seniority_val)
        this_seniority_val = round(this_seniority_val, 1)
        this_seniority_val = str(this_seniority_val)
        return this_seniority_val

    def getInsertData(self, unique_val, table_name, data_list, num):
        '''
        get insert data and update data
        '''

        unique_list = self.dml_obj.selectData(unique_val, table_name)
        db_code_list = [code_tupe[0] for code_tupe in unique_list]
        insert_data = []
        update_data = []
        excel_danhao_data = []
        for each_list in data_list:
            excel_danhao_data.append(each_list[num].encode("UTF-8"))
            if each_list[num].encode("UTF-8") in db_code_list:
                update_data.append(each_list)
            else:
                this_list = []
                this_list.extend(each_list)
                insert_data.append(this_list)
        # 遍历 数据库和表是否一致, 表中不存在的删除
        for data in db_code_list:
            if data not in excel_danhao_data:
                # print "deleteData: ", data
                self.dml_obj.deleteData(GeneralParameters.demand_table, "d_number = '{}'".format(data))

        return insert_data, update_data

    def getEmployeeInsertData(self, unique_val, table_name, data_list, num):
        '''
        get insert data and update data
        '''
        unique_list = self.dml_obj.selectData(unique_val, table_name)

        db_code_list = [code_tupe[0] for code_tupe in unique_list]
        insert_data = []
        update_data = []

        for each_list in data_list:
            if each_list[num].encode("UTF-8") in db_code_list:
                update_data.append(each_list)
            else:
                this_list = []
                this_list.extend(each_list)
                this_list.append(u"常設")
                insert_data.append(this_list)
        return insert_data, update_data

    def getRecruitInsertData(self, unique_val, table_name, data_list, num):
        '''
        get insert data and update data
        '''
        unique_list = self.dml_obj.selectData(unique_val, table_name)
        db_code_list = []
        db_interview_list = []
        for code_tupe in unique_list:
            r_number_val = code_tupe[0]
            r_Idcard_val = code_tupe[1]
            r_interview_val = code_tupe[2]
            db_code_list.append([r_number_val, r_Idcard_val])
            db_interview_list.append(r_interview_val)
        insert_data = []
        update_data = {}
        for each_list in data_list:
            number_val = str(each_list[num]).encode("UTF-8")
            name_val = str(each_list[4]).encode("UTF-8")
            this_list = [number_val, name_val]
            if this_list in db_code_list:
                db_interview_val = db_interview_list[db_code_list.index(this_list)]
                if each_list[6] >= db_interview_val:
                    if name_val in update_data.keys():
                        old_list = update_data[name_val]
                        if int(each_list[1]) == int(old_list[1]):
                            if each_list[6] >= old_list[6]:
                                update_data[name_val] = each_list
                        elif int(each_list[1]) > int(old_list[1]):
                            update_data[name_val] = each_list
                    else:
                        update_data[name_val] = each_list
            else:
                insert_data.append(each_list)
        return insert_data, update_data

    def getFK(self, fk_table_id, fk_name, this_fk_val, fk_table):
        '''
        get fk's id
        '''
        if not this_fk_val:
            return None
        fk_val_list = self.dml_obj.selectData(fk_table_id, fk_table, fk_name + " = '" + this_fk_val + "'")
        if not fk_val_list:
            fk_val = None
        else:
            fk_val = fk_val_list[0][0]
        return fk_val

    def getUpdateFK(self, fk_table_id, fk_name, this_fk_val, fk_table):
        '''
        get fk's id
        '''
        if not this_fk_val:
            return ""
        fk_val_list = self.dml_obj.selectData(fk_table_id, fk_table, fk_name + " = '" + this_fk_val + "'")
        if not fk_val_list:
            fk_val = ""
        else:
            fk_val = str(fk_val_list[0][0])
        return fk_val

    def emptyData(self):
        """
        delete data
        """
        self.dml_obj.emptyTable(GeneralParameters.deputy_table)
        self.dml_obj.emptyTable(GeneralParameters.employee_table)
        self.dml_obj.emptyTable(GeneralParameters.line_table)
        self.dml_obj.emptyTable(GeneralParameters.group_table)
        self.dml_obj.emptyTable(GeneralParameters.subject_table)
        self.dml_obj.emptyTable(GeneralParameters.department_table)
        self.dml_obj.emptyTable(GeneralParameters.bureau_table)
        print "Finished delete data!"

    def printList(self, t_list):
        for l in t_list:
            print l, type(l)

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

    def changeReplace(self, old_val):
        '''
        @note: 
        '''
        old_val = old_val.replace(" ", "")
        old_val = old_val.replace("&", "")
        old_val = old_val.replace("/", "")
        old_val = old_val.replace("$", "")
        return old_val

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

    def add_E_firsrdate(self):
        '''
        @note: 查詢五月后新增且e_firstdate為空的數據， 將其e_firstdate的值就設置為create_time
        '''
        employee_id_tuple = self.dml_obj.selectData("E_ID", GeneralParameters.employee_table,
                                                    "e_id is not null and CREATE_TIME >= to_date('2019-05-01','yyyy-mm-dd')")
        employee_id_list = [id_tuple[0] for id_tuple in employee_id_tuple]
        for employee_id in employee_id_list:
            res = self.dml_obj.selectData("E_FIRSTDATE, CREATE_TIME", GeneralParameters.employee_table,
                                          "e_id='{}'".format(employee_id))
            if not res:
                continue
            first_time, create_time = res[0]
            if not first_time:
                update_string = 'update ' + GeneralParameters.employee_table + (
                    " set e_firstdate=to_date('{}','yyyy-mm-dd hh24:mi:ss') where e_id = '{}'").format(str(create_time),
                                                                                                       employee_id)
                self.dml_obj.updateData(update_string)
            else:
                continue

    def insertExcel(self):
        """每日生成人力工號信息模板--> 给考勤异常爬虫用的"""
        self.file_object.write("\n ---------------------EmpNo.xls 异常考勤工号信息----------------------- \n")
        self.writeTxt("insert EmpNo.xls 异常考勤工号信息", "Beginning")
        # 需要xlwt库的支持
        # import xlwt
        # 指定file以utf-8的格式打开
        file = Workbook(encoding='utf-8')
        # 指定打开的文件名
        table = file.add_sheet('data')
        today_start_time = datetime.strptime(str(datetime.now()).split(" ")[0] + " 00:00:00", '%Y-%m-%d %H:%M:%S')
        today_end_time = datetime.strptime(str(datetime.now()).split(" ")[0] + " 23:59:59", '%Y-%m-%d %H:%M:%S')
        # 从数据库取最新人力工号信息
        emlpoyee_sql = "edit_time between to_date('%s', 'yyyy-mm-dd hh24:mi:ss') and  to_date('%s', 'yyyy-mm-dd hh24:mi:ss')" % (
            today_start_time, today_end_time)
        emlpoyee_obj = self.dml_obj.selectData("e_id", GeneralParameters.employee_table, emlpoyee_sql)
        # 列表数据
        data = list(zip(*emlpoyee_obj)[0])

        ldata = []
        num = [a for a in data]

        # 字典数据取出后无需，需要先排序
        num.sort()

        # 添加第一行為 工號
        num.insert(0, "工號")

        for x in num:
            # for循环将data字典中的键和值分批的保存在ldata中
            ldata.append(x)
        j = 0
        for i, p in enumerate(ldata):
            # 将数据写入文件,i是enumerate()函数返回的序号数
            print i, j, p
            table.write(i, j, p)
        # 文件保存路径
        file.save(GeneralParameters.EmpNo_Excel_path)
        logging.info("Finished insertEmpNo!!")
        self.writeTxt("EmpNo.xls生成成功", "Finished")


if __name__ == '__main__':
    instance = ArrangeData()
