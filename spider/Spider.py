# encoding:utf-8
"""
@Create Time: 2019/12/2 上午 09:49
@Description:
"""
import os
import logging
import time
import ConfigParser
from General import General
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from functools import wraps


def retry_for_errors(errors=Exception, retry_times=5, poll_time=10):
    """
    Decorator to retry for multiple errors.
    Example::
        @retry_for_errors(errors=(RuntimeError,NameError))
        def func():
            pass
    """
    assert retry_times > 0, 'retry_times must larger than 0!'

    def wrapper_(func):
        @wraps(wrapped=func)
        def wrapper(self, *args, **kwargs):
            retry = 1
            while retry <= retry_times:
                try:
                    return func(*args, **kwargs)
                except errors as exc:
                    msg = "Retry for {} for {} time...".format(exc, retry)
                    print(msg)
                    retry += 1
                    if retry > retry_times:
                        raise exc
                    else:
                        time.sleep(poll_time)
        return wrapper
    return wrapper_


class Spider(object):
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.set_log()
        logging.info('start :' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

        self.eisp_url, self.download_path = self.read_config()
        self.create_folder()
        self.driver = self.config_browser()
        self.run_chrome('register')

    @staticmethod
    def read_config():
        """
        @note: read config.ini file
        @note: get all config parameters
        :return:
        """
        # 读配置文件  config.ini
        cf = ConfigParser.ConfigParser()
        cf.read(General.config_file_path)
        # 配置文件用户账号
        eisp_username = cf.get(General.ie_section, General.eisp_username_option)
        eisp_password = cf.get(General.ie_section, General.eisp_password_option)
        eisp_url = cf.get(General.ie_section, General.eisp_html)
        eisp_url = eisp_url % (eisp_username, eisp_password)
        data_path = cf.get(General.ie_section, General.data_path)
        time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
        download_path = os.path.join(data_path, time_str)
        return eisp_url, download_path

    def config_browser(self):
        """
        @note: config the chrome browser
        @note: open
        selenium驱动启动
        :return:
        """
        logging.info('config browser')
        options = webdriver.ChromeOptions()
        # disable pop the window and set the download default directory
        # 定制启动Chrome选项
        # options.binary_location = General.binary_location  # chrome启动选择
        # profile.default_content_settings.popups：设置为 0 禁止弹出窗口
        # download.default_directory：设置下载路径
        prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': self.download_path}
        options.add_experimental_option('prefs', prefs)
        # 忽视缺证书警告
        options.add_argument('test-type')
        # 启动Chrome浏览器
        driver = webdriver.Chrome(General.chrome_driver_path, chrome_options=options)
        return driver

    # @retry_for_errors
    def run_chrome(self, flag):
        self.driver.get(self.eisp_url)
        logging.info('open: ' + self.eisp_url)
        time.sleep(5)
        self.driver.get(General.eisp_url)
        self.driver.maximize_window()
        # click login
        self.get_element(self.driver, By.XPATH, General.login_btn_xpath, timeout=60).click()
        logging.info('login eisp')
        time.sleep(5)
        # click 快速查询
        self.get_element(self.driver, By.XPATH, General.quick_search_xpath, timeout=60).click()
        logging.info(u'click 快速查询')
        time.sleep(5)
        # click 经管类表单
        self.get_element(self.driver, By.XPATH, General.management_form_xpath, timeout=60).click()
        logging.info(u'click 经管类表单')
        time.sleep(5)
        # 切换frame
        self.driver.switch_to.frame(General.frame_id)
        logging.info('switch to subframe')
        time.sleep(1)
        # click 金石专案结案申请单
        if flag == 'settled':
            self.get_element(self.driver, By.XPATH, General.settled_application_xpath, timeout=60).click()
            logging.info(u'click 金石专案结案申请单')
        elif flag == 'register':
            self.get_element(self.driver, By.XPATH, General.register_application_xpath, timeout=60).click()
            logging.info(u'click 金石专案立案申请单')
        time.sleep(5)
        # 设置日期
        start_date = str(time.localtime().tm_year)+'-1-1'
        # 立案开始日期
        register_ele = self.get_element(self.driver, By.XPATH, General.register_date_xpath, timeout=60)
        register_ele.clear()
        register_ele.send_keys(start_date)
        logging.info(u'设置立案日期:' + start_date)
        time.sleep(2)
        # 创建日期
        create_ele = self.get_element(self.driver, By.XPATH, General.create_date_xpath, timeout=60)
        create_ele.clear()
        create_ele.send_keys(start_date)
        logging.info(u'设置创建日期:' + start_date)
        time.sleep(2)
        # 最后修改日期
        update_ele = self.get_element(self.driver, By.XPATH, General.update_date_xpath, timeout=60)
        update_ele.clear()
        update_ele.send_keys(start_date)
        logging.info(u'设置最后修改日期:' + start_date)
        time.sleep(2)
        # 设置 立案bu--选择 周邊
        bu_select_ele = self.get_element(self.driver, By.XPATH, General.bu_select_xpath, timeout=60)
        bu_select_ele.click()
        logging.info(u'click 立案bu')
        options = bu_select_ele.find_elements_by_xpath('.//option')
        for op in options:
            if op.text == General.select_option:
                op.click()
                logging.info(u'click: 周邊')
                break
        time.sleep(5)
        # click 查询
        # self.get_element(self.driver, By.XPATH, General.search_xpath, timeout=60).click()
        # time.sleep(10)
        # click 导出
        self.get_element(self.driver, By.XPATH, General.export_xpath, timeout=60).click()
        logging.info(u'click 导出')
        time.sleep(10)
        while True:
            if os.listdir(self.download_path):
                logging.info('Download success')
                break

        self.close_browser()
        logging.info('run chrome done close browser')

    def close_browser(self):
        """close selenium browser"""
        try:
            self.driver.quit()
        except Exception as e:
            logging.exception('Got exception on close browser')

    def login_eisp(self):
        pass

    def create_folder(self):
        # data_path = os.path.join(self.base_dir, 'data')
        # if not os.path.isdir(data_path):
        #     os.makedirs(data_path)
        # time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
        # download_path = os.path.join(data_path, time_str)
        # os.makedirs(download_path)
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        logging.info('create folder ' + self.download_path)

    def set_log(self):
        """设置日志"""
        log_path = os.path.join(self.base_dir, 'golden_stone_project.log')
        print(log_path)
        # 初始化日志对象
        logging.basicConfig(
            # 日志文件存放目录
            filename=log_path,
            # 日志等级
            level=logging.INFO,
            # 日志格式 时间、代码所在文件名    日志级别名字      日志信息
            format='%(asctime)s : %(levelname)s : %(message)s')

    @staticmethod
    def get_element(driver, ele_index, ele_val, timeout=300, poll_frequency=0.5):
        """
        @note: get element when element display.
        """
        _element = WebDriverWait(driver, timeout, poll_frequency).until(
            EC.presence_of_element_located((ele_index, ele_val))
        )
        return _element


if __name__ == '__main__':
    Spider()
