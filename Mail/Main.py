# encoding:utf-8
"""
@Create Time: 2019/12/9 上午 08:57
@Author: 
@Description:
"""
import os
import logging
import psutil
import time
import ConfigParser
from datetime import datetime
from DMLData import oracle
from SuperNotes import SuperNotes
from General import General
from itertools import chain
from demo import open_excel


class Spider(object):
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        print('base dir:', self.base_dir)
        self.set_log()
        self.dml_obj = oracle()
        self.mail_info = self.read_config()
        self.sn = SuperNotes()
        self.xlsx_path = self.get_gsp_data()
        # self.run_()

    def get_gsp_data(self):
        this_year = str(datetime.now().year)
        this_year_data = self.dml_obj.selectData('e_leader, e_functionteam, e_team_target, e_register_num, e_no_closed_num, e_closed_num, e_performance, e_team_hc',
                                                 'egspbyleader', "e_year='" + this_year + "'")
        team_table_data = []
        leader_num_dict = {}
        eerf_total = {}
        for data in this_year_data:
            each_team_data = []
            each_team_data.append(data[1])
            each_team_data.append(data[5])
            each_team_data.append(data[2])
            team_table_data.append(each_team_data)
            if 'eerf' not in eerf_total.keys():
                eerf_total['eerf'] = data[2:]
            else:
                eerf_total['eerf'] = [i + j for i, j in zip(eerf_total['eerf'], data[2:])]
            if data[0] not in leader_num_dict.keys():
                leader_num_dict[data[0]] = data[2:]
            else:
                leader_num_dict[data[0]] = [i + j for i, j in zip(leader_num_dict[data[0]], data[2:])]
        # 按照 结案已发起 数量 降序排序
        team_table_data = sorted(team_table_data, key=lambda x: x[1], reverse=True)
        team_table_data.insert(0, ['Function Team', u'結案 已發起', u'建議年度目標 '])
        # 按照 结案已发起 数量 降序排序
        leader_num_list = sorted(leader_num_dict.items(), key=lambda v: v[1][1], reverse=True)
        eerf_total['eerf'].insert(0, 'EERF')
        table_data = []
        for t in leader_num_list:
            _ = []
            _.append(t[0])
            _.extend(t[1])
            # 结案金额比例
            amount_ratio = _[5]/eerf_total['eerf'][5]
            # 人均效益
            per_benefit = _[5]/_[6]
            _.insert(6, amount_ratio)
            _.insert(7, per_benefit)
            table_data.append(_)
        # table_data = [list(chain(x[0], x[1])) for x in table_data]
        eerf_total['eerf'].insert(6, 1)
        eerf_total['eerf'].insert(7, eerf_total['eerf'][5]/eerf_total['eerf'][7])
        # x = eerf_total['eerf'][:6]
        # x.append(1)
        # x.append(eerf_total['eerf'][5]/eerf_total['eerf'][6])
        table_data.append(eerf_total['eerf'])
        title = [u'Leader', u'建議年度目標 ', u'立案 已完成', u'結案 未發起', u'結案 已發起',
                 u'預估結案 總金額(萬RMB)', u'預估結案 金額比例', u'預估結案 人均效益(萬RMB)', u'年初人数']
        table_data.insert(0, title)
        # self.xlsx_path = self.base_dir + '/' + 'gsp.xlsx'
        xlsx_path = os.path.join(self.base_dir, 'gsp.xlsx')
        self.sn.OpenExcel(table_data, xlsx_path, 'Summary', second_table_data=team_table_data)
        # open_excel(xlsx_path, 'Summary')
        return xlsx_path

    def run_(self):
        try:
            this_year, this_mouth, prior_year, prior_mouth = self.getYearMouth()
            mail_title = u'EERF金石专案数量统计'
            content_list = [u'Dear All:',
                            u'截至' + str(this_year) + u'年' + str(this_mouth) + u'月' + str(01) + u'日, 金石专案申请数量如下圖',
                            [], self.xlsx_path]
            flag = self.send_mail(mail_title, content_list)
            while not flag:
                try:
                    self.kill_process('SuperNotes.exe')
                except:
                    pass
                flag = self.send_mail(mail_title, content_list)
            self.sn.close()
            logging.info(u'End Send 金石专案数量统计 mail')
        except Exception as e:
            logging.exception('Got exception on run')

    def send_mail(self, mail_title, content_list):
        flag = True
        try:
            logging.info('Beginning sendMail!!!')
            logging.info(self.mail_info['mail_path'])

            self.sn.login(self.mail_info['mail_path'], self.mail_info['mail_username'], self.mail_info['mail_password'])
            logging.info('login mail')
            message_dic = {'To': self.mail_info['to_mailusers'], 'Cc': self.mail_info['cc_mailusers'], 'Title': mail_title,
                           'Content': content_list}
            self.sn.send_notes(message_dic)
        except:
            logging.exception('Got exception on send mail')
            flag = False
            logging.info('kill super notes and restart')
        return flag

    def kill_process(self, process_name):
        """杀掉进程 SuperNotes.exe mspaint.exe"""
        sn_pid = None
        pids = psutil.pids()
        for pid in pids:
            p = psutil.Process(pid)
            # print("pid-%d,pname-%s" %(pid, p.name()))
            if p.name() == process_name:
                sn_pid = pid
                break
        if sn_pid:
            try:
                import subprocess
                subprocess.Popen("cmd.exe /k taskkill /F /T /PID %i" % sn_pid, shell=True)
            except OSError, e:
                # print 'no process'
                # logging.info('kill %s process error:' % process_name)
                logging.exception('Got exception on kill' + process_name +' process')

    def read_config(self):
        cf = ConfigParser.ConfigParser()
        cf.read(General.config_file_path)
        info = {}
        info['mail_path'] = cf.get(General.ie_section, General.mail_path)
        info['mail_username'] = cf.get(General.ie_section, General.mail_username)
        info['mail_password'] = cf.get(General.ie_section, General.mail_password)
        info['to_mailusers'] = cf.get(General.ie_section, General.to_mailusers)
        info['cc_mailusers'] = cf.get(General.ie_section, General.cc_mailusers)
        return info

    @staticmethod
    def getYearMouth():
        """
        @note: 获取 今年的年月和去年的年月 int
        """
        this_year = time.localtime().tm_year
        this_month = time.localtime().tm_mon
        this_day = time.localtime().tm_mday
        if this_month == 1:
            prior_year = this_year - 1
            if this_day < 5:
                prior_month = 11
            else:
                prior_month = 12
        else:
            prior_year = this_year
            if this_day < 5:
                prior_month = this_month - 2
            else:
                prior_month = this_month - 1
        return this_year, this_month, prior_year, prior_month

    def set_log(self):
        log_path = os.path.join(self.base_dir, 'gsp.log')
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s : %(filename)s/%(lineno)s:%(levelname)s: %(message)s')


if __name__ == '__main__':
    Spider()
