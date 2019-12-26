# encoding:utf-8
"""
@Create Time: 2019/12/9 上午 08:57
@Author: 
@Description:
"""
import logging
import win32gui
from datetime import datetime
from time import sleep
import win32com.client as win32
import xlsxwriter
from pywinauto import application
from pywinauto.SendKeysCtypes import SendKeys
import traceback

titles = set()


class SuperNotes(object):
    def __init__(self):
        print("Beginning Super_Notes!!!!")

    @staticmethod
    def lwfoo2(hwnd, mouse):
        # 去掉下面这句就所有都输出了，但是我不需要那么多
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            titles.add(win32gui.GetWindowText(hwnd))

    def login(self, mail_path, username, password):
        """
        @note:
        :return:
        """
        self.app = application.Application.start(mail_path)
        sleep(15)

        sleep(3)
        top_dlg = self.app.top_window_()
        sleep(2)
        top_dlg["Edit1"].TypeKeys(username)
        top_dlg["Edit2"].TypeKeys(password)
        sleep(2)
        # print top_dlg.print_control_identifiers()
        logging.info('login.........')
        top_dlg[u'確定'].Click()
        sleep(50)
        SendKeys("{ENTER}")
        sleep(50)

    def send_notes(self, message={}):
        """
        @note: message_dic requisite keys 'To','Cc','Title','Content'
        """
        if 'To' in message.keys():
            SendKeys("^M")
            sleep(15)
            top_dlg = self.app.top_window_()
            # print top_dlg.print_control_identifiers()
            sleep(1)
            top_dlg["Edit4"].TypeKeys(message['To'])
            if 'Cc' in message.keys():
                top_dlg["Edit3"].TypeKeys(message['Cc'])
            top_dlg["Edit0"].TypeKeys(message['Title'])
            SendKeys("{TAB}")
            SendKeys("{TAB}")
            self.writeContent(message['Content'], top_dlg)
            sleep(30)
            top_dlg['Button5'].Click()
            top_dlg['Button10'].Click()
            # print top_dlg.print_control_identifiers()
            if 'Doc' in message.keys():
                self.add_doc(message['Doc'])
            SendKeys('%A')
            sleep(2)
            SendKeys('{ENTER}')
            sleep(60)

    def writeContent(self, content, top_dlg):
        """
        @note: content = [0, 1, 2, 3,...]
        """
        top_dlg['ComboBox1'].TypeKeys("%{DOWN}")
        top_dlg['ComboBox1'].Select(u'微軟正黑體')
        # 4--14 5--18
        sleep(0.5)
        top_dlg['ComboBox2'].TypeKeys('5')
        sleep(0.5)
        top_dlg["Edit0"].TypeKeys("")
        SendKeys('{TAB}')
        SendKeys('{TAB}')
        sleep(0.5)

        head = content[0].split(' ')
        for h in head:
            SendKeys(h)
            if h != head[-1]:
                SendKeys('{ }')
        SendKeys('{ENTER}')
        SendKeys('{ENTER}')
        SendKeys('{TAB}')

        SendKeys(u'正')

        top_dlg['ComboBox1'].TypeKeys("%{DOWN}")
        top_dlg['ComboBox1'].Select(u'微軟正黑體')
        # 4--14 5--18
        sleep(0.5)
        top_dlg['ComboBox2'].TypeKeys('5')
        sleep(0.5)
        top_dlg["Edit0"].TypeKeys("")
        SendKeys('{TAB}')
        SendKeys('{TAB}')
        sleep(0.5)

        SendKeys(content[1])
        for x in range(len(content[1]) - 1):
            SendKeys('{LEFT}')
        SendKeys('{BACKSPACE}')
        for y in range(len(content[1]) - 1):
            SendKeys('{RIGHT}')
        SendKeys('{ENTER}')
        SendKeys('{TAB}')
        SendKeys('{ENTER}')
        sleep(5)
        if content[3]:
            if 'attendanceExcel' in content[3]:
                wb = self.getFailimg(content[3], [u'准点下班人数', "A1:H25"])
                wb.Save()
            elif 'dimissionExcel' in content[3]:
                wb = self.getFailimg(content[3], [u'離職狀況', "A1:E10"])
                wb.Save()
            elif 'gsp' in content[3]:
                wb = self.getFailimg(content[3], ['Summary', "A1:H10"])
                wb.Save()
            sleep(15)
            try:
                wb.close()
            except:
                pass
            SendKeys('{ENTER}')
            sleep(10)
        if len(content[2]) > 0:
            self.insertImg(content[2], top_dlg)

    @staticmethod
    def insertImg(img_path, top_dlg):
        """
        @note:
        """
        for i, i_p in enumerate(img_path):
            # SendKeys('{RIGHT}')
            if i >= 1:
                top_dlg["Edit0"].TypeKeys("")
                SendKeys('{TAB}')
                SendKeys('{TAB}')
                SendKeys('{ENTER}')
                # SendKeys('{ENTER}')

            top_dlg['ComboBox2'].TypeKeys('5')
            for x in range(6):
                SendKeys('{TAB}')
                sleep(0.5)

            SendKeys('{ENTER}')
            sleep(1)
            SendKeys(i_p)
            sleep(1)
            SendKeys('{ENTER}')
            sleep(2)
            # SendKeys('{ENTER}')
            # sleep(2)
            # top_dlg["Edit0"].TypeKeys('')
            # SendKeys('{TAB}')
            # SendKeys('{TAB}')
            sleep(10)

    @staticmethod
    def OpenExcel(table_list, table_data_path, sheet_name, second_table_data=None):
        """
        @note: 写入 Excel
        """
        logging.info("Beginning OpenExcel------")
        workbook = xlsxwriter.Workbook(table_data_path)
        worksheet = workbook.add_worksheet(sheet_name)

        # workbook.add_format({'bold':True})
        property = {
            'font_size': 14,  # 字体大小
            'bold': True,  # 是否加粗
            'border': 1,
            'align': 'center ',  # 水平对齐方式
            'valign': 'center',  # 垂直对齐方式
            'font_name': u'微軟正黑體',
            'text_wrap': True,  # 是否自动换行
            'bg_color': '#808080',
            'font_color': '#FFFFFF'
        }
        fristRow = workbook.add_format(property)
        for col, colData in enumerate(table_list[0]):
            worksheet.set_column(0, 9, 23.75)
            worksheet.set_row(0, 40)
            worksheet.write(0, col, colData, fristRow)
        # set_row(row, height, ceel_format, options)

        property['bold'] = False
        property['font_color'] = "#000000"
        colorList = ['#808080', '#DDD9C3', '#C5D9F1', '#F2DDDC', '#EAF1DD',
                     '#E5E0EC', '#F2DDDC', '#DBEEF3', '#FDE9D9', '#FFFFFF']
        for row, rowDatas in enumerate(table_list):
            if row >= 1:
                index_val = row
                if row >= len(colorList):
                    index_val = row - len(colorList)
                property['bg_color'] = colorList[index_val]
                otherRow = workbook.add_format(property)
                worksheet.set_row(row, 20)
                for col, colData in enumerate(rowDatas):
                    worksheet.write(row, col, colData, otherRow)

        if second_table_data:
            for i, title in enumerate(second_table_data[0]):
                worksheet.set_column(10, 13, 23.75)
                # worksheet.set_row(0, 40)
                worksheet.write(0, i+9, title, fristRow)
            for j, row_data in enumerate(second_table_data):
                if j >= 1:
                    s_index_val = j
                    if j >= len(colorList):
                        s_index_val = j - len(colorList)
                    property['bg_color'] = colorList[s_index_val%10]
                    otherRow = workbook.add_format(property)
                    worksheet.set_row(j, 20)
                    for k, cell_data in enumerate(row_data):
                        worksheet.write(j, k+9, cell_data, otherRow)

        column_chart = workbook.add_chart({'type': 'column'})
        # chart.add_series({'values': '=Sheet1!$A$1:$A$5'})
        column_chart.add_series({'values': '=Summary!$B$2:$B$10', 'categories': '=Summary!$A$2:$A$10',
                          'name': u'建议年度目标', 'data_labels': {'value': True}})
        column_chart.add_series(
            {'values': '=Summary!$C$2:$C$10', 'categories': '=Summary!$A$2:$A$10',
             'name': u'立案 已完成', 'data_labels': {'value': True}})
        column_chart.add_series(
            {'values': '=Summary!$D$2:$D$10', 'categories': '=Summary!$A$2:$A$10',
             'name': u'结案 未发起', 'data_labels': {'value': True}})
        # 设置legend的位置在图下方
        column_chart.set_legend({'position': 'bottom'})
        # 设置不显示网格线
        column_chart.set_y_axis({'major_gridlines': {'visible': False}})
        # column_chart.set_style(15)
        pie_chart = workbook.add_chart({'type': 'pie'})
        # position: outside_end
        pie_chart.add_series(
            {'values': '=Summary!$G$2:$G$10', 'categories': '=Summary!$A$2:$A$10',
             'name': u'預估結案 金額比例', 'data_labels':{'value':True, 'category':True, 'position': 'best_fit',
                                                        'num_format': '0.00%', 'leader_lines': True}})

        pie_chart.set_legend({'none': True, 'position': 'top'})
        radar_chart = workbook.add_chart({'type': 'radar', 'subtype': 'filled'})
        radar_chart.add_series(
            {'values': '=Summary!$H$2:$H$10', 'categories': '=Summary!$A$2:$A$10',
             'name': u'預估結案 人均效益（萬 RMB）', 'data_labels': {'value': True, 'num_format': '#,##0.00'}})
        radar_chart.set_legend({'position': 'bottom'})
        # pie_chart.set_style(14)
        # line_chart = workbook.add_chart({'type': 'line'})
        # line_chart.add_series({'values': '=GoldenStoneProject!$C$2:$C$10', 'categories': '=GoldenStoneProject!$A$2:$A$10',
        #                   'name': u'金石专案目标数量', 'data_labels': {'value': True}})
        # column_chart.combine(line_chart)
        worksheet.insert_chart('A13', column_chart, {'x_scale': 1.45, 'y_scale': 2.7})
        worksheet.insert_chart('E13', pie_chart, {'x_scale': 1.42, 'y_scale': 1.38})
        worksheet.insert_chart('E29', radar_chart, {'x_scale': 1.42, 'y_scale': 1.32})
        workbook.close()
        logging.info("Finished OpenExcel------")

    @staticmethod
    def create_attendance_excel(table_list, table_data_path, sheet_name):
        """@note: 写入 Excel"""
        # table_list = [['Leader', u'非準點下班（%）', u'同比上月（%）'], ['leader-a', 1, 2], ['leader-b', 3, 5],
        # ['leader-c', 2, 7], ['leader-d', 78, 8], ['leader-e', 78, 8], ['leader-f', 78, 8], ['leader-g', 78, 8]]

        workbook = xlsxwriter.Workbook(table_data_path)
        worksheet = workbook.add_worksheet(sheet_name)

        property = {
            'font_size': 14,  # 字体大小
            'bold': True,  # 是否加粗
            'border': 1,
            'align': 'center ',  # 水平对齐方式
            'valign': 'vcenter',  # 垂直对齐方式
            'font_name': u'微軟正黑體',
            'text_wrap': False,  # 是否自动换行
            'bg_color': '#808080',
            'font_color': '#FFFFFF',  # 字体颜色
        }
        fristRow_format = workbook.add_format(property)
        fristRow_format.set_align('center')
        fristRow_format.set_align('vcenter')
        for col, colData in enumerate(table_list[0]):
            worksheet.set_column(0, 3, 23.75)
            worksheet.set_column(2, 2, 28.5)
            # 设置function team 这一列宽度
            worksheet.set_column(4, 4, 33)
            worksheet.set_column(5, 8, 23.75)
            worksheet.set_column(6, 6, 28.5)
            worksheet.set_row(0, 20)
            worksheet.write(0, col, colData, fristRow_format)

        property['bold'] = False
        property['font_color'] = "#000000"
        colorList = ["#808080", "#DDD9C3", "#C5D9F1", "#F2DDDC", "#EAF1DD",
                     "#E5E0EC", "#F2DDDC", "#DBEEF3", "#FDE9D9", "#FFFFFF"]

        num = 0
        for row, rowDatas in enumerate(table_list):
            if row >= 1:
                index_val = row
                if row >= len(colorList):
                    index_val = row - len(colorList)
                property['bg_color'] = colorList[index_val]
                otherRow_format = workbook.add_format(property)
                otherRow_format.set_align('center')
                otherRow_format.set_align('vcenter')
                worksheet.set_row(row, 20)
                for col, colData in enumerate(rowDatas):
                    if col <= 3:
                        if len(rowDatas[4]) > 1:
                            worksheet.merge_range(row + num, col, row + num + len(rowDatas[4]) - 1, col, colData,
                                                  otherRow_format)
                        else:
                            worksheet.write(row + num, col, colData, otherRow_format)
                    else:
                        for i, team_data in enumerate(colData):
                            for j, cell_data in enumerate(team_data):
                                worksheet.write(row + num + i, col + j, cell_data, otherRow_format)
                num += len(rowDatas[4]) - 1

        workbook.close()
        print('Write attendance Excel Done!')

    @staticmethod
    def add_doc(file_path):
        """
        @note:
        """
        SendKeys('%A')
        SendKeys('{DOWN}')
        SendKeys('{DOWN}')
        SendKeys('{DOWN}')
        SendKeys('{DOWN}')
        SendKeys('{ENTER}')
        sleep(2)
        SendKeys(file_path)
        SendKeys('{ENTER}')

    @staticmethod
    def close():
        """
        @note:
        :return:
        """
        SendKeys("%F")
        sleep(1)
        SendKeys('{UP}')
        sleep(1)
        SendKeys('{ENTER}')
        sleep(1)
        SendKeys('{ENTER}')

    def OpenMspaint(self, mspaintPath, imgPath):
        """
        @note: 小画家
        """
        flag = True
        try:
            logging.info('Beginning OpenMspaint!!!')
            Mspaint = application.Application.start(mspaintPath)
            sleep(10)
            SendKeys("^O")
            sleep(10)
            SendKeys(imgPath)
            sleep(4)
            SendKeys("{ENTER}")
            sleep(5)

            # 调整像素
            SendKeys("^W")
            sleep(10)
            top_dlg = Mspaint.top_window_()
            sleep(2)
            top_dlg[u'百分比'].Click()
            sleep(2)
            top_dlg["Edit1"].SetEditText('98')
            sleep(2)
            top_dlg[u'確定'].Click()
            sleep(3)

            SendKeys("^S")
            sleep(10)
            SendKeys("%{F4}")
            logging.info('Finished OpenMspaint!!!')
        except:
            flag = False
            logging.info('Open Mspaint exception')
            logging.info(traceback.format_exc())
        return flag

    @staticmethod
    def getFailimg(file_path, data):
        """
        @note: 将 excel 内的表格制作成图片
        """
        excel = win32.Dispatch('Excel.Application')
        logging.info(file_path)
        wb = excel.Workbooks.open(file_path)
        ws = wb.Worksheets(data[0])
        ws.Range(data[1]).CopyPicture('1', '2')
        ws.Paste(ws.Range("Y1"))
        ws.Shapes("Picture 1").copy()
        sleep(1)
        SendKeys("^V")
        sleep(10)
        SendKeys('{ENTER}')
        SendKeys('{ENTER}')
        # 复制team表格数据
        ws.Range("J1:L25").CopyPicture('1', '2')
        ws.Paste(ws.Range("Y1"))
        ws.Shapes("Picture 2").copy()
        sleep(1)
        SendKeys("^V")
        sleep(10)
        SendKeys('{ENTER}')
        SendKeys('{ENTER}')
        # 复制3张图片
        ws.Range("A13:H47").CopyPicture('1', '2')
        ws.Paste(ws.Range("Y1"))
        ws.Shapes("Picture 3").copy()
        sleep(1)
        SendKeys("^V")
        sleep(10)
        SendKeys('{ENTER}')
        SendKeys('{ENTER}')
        # copy image
        # ws.Shapes('Chart 1').copy()
        # sleep(1)
        # SendKeys("^V")
        # sleep(10)
        # SendKeys('{ENTER}')
        return wb


if __name__ == '__main__':
    S_N = SuperNotes()
    #     S_N.OpenExcel([], r"C:\Users\F1233084\Downloads\attendanceExcel.xlsx")
    #
    #     S_N.OpenMspaint("C:\Windows\System32\mspaint.exe", "C:\Users\F1233084\Downloads\download_1543221967490.png")
    #     print "Finished OpenMspaint!!!!"
    img_list = [r'D:\PySpace\Recruit_SendMail-Attendance\download_1564705510484.png',
                r'D:\PySpace\Recruit_SendMail-Attendance\download_1564705536191.png']
    # S_N.login(r'C:\Program Files (x86)\Super Notes\SuperNotes.exe', 'luke.xf.zhang@mail.foxconn.com', 'Asdf123.')
    message_dic = {}
    message_dic['To'] = 'luke.xf.zhang@mail.foxconn.com'
    message_dic['Cc'] = 'luke.xf.zhang@mail.foxconn.com'
    message_dic['Title'] = u'EERF-2019年6月-師級考勤狀況[本郵件為系統郵件，請勿直接回復]'
    message_dic['Content'] = [u'Dear All:', u'截至2019年8月1日, 師級考勤狀況如下圖', u'最佳瀏覽器使用Chrome v58.0以上版本',
                              img_list, r"D:\PySpace\Recruit_SendMail-Attendance\attendanceExcel.xlsx"]
    # S_N.send_notes(message_dic)
    S_N.getFailimg(r"D:\PySpace\Recruit_SendMail-Attendance\attendanceExcel.xlsx", "A1:F25")
    S_N.close()
