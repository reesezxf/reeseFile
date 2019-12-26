# encoding:utf-8
"""
@Create Time: 2019/12/9 下午 04:36
@Author: 
@Description:
"""
import os


class General(object):
    config_file_path = os.path.join(os.path.dirname(__file__), 'config\config.ini')
    ie_section = 'ie_detail'
    mail_section = 'mail_pfa'
    mail_path = 'mail_path'
    mail_username = 'mail_username'
    mail_password = 'mail_password'
    to_mailusers = 'To_mailusers'
    cc_mailusers = 'Cc_mailusers'
    bcc_mailusers = 'BCC_mailusers'
