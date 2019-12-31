# -*- coding:utf-8 -*-
"""
big5

some files have html table format
get the data form these files
author : sara
"""
import os
import re
import chardet, urllib ,numpy
import xlsxwriter
from HTMLParser import HTMLParser
SWNA = u"SWNA"


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):

        if tag == "table":
            self.row_num = 0
            self.col_num = 0
            self.table_data = []
        elif tag == "tr":
            if self.row_num < len(self.table_data):
                self.table_data_tr = self.table_data[self.row_num]
            else:
                self.table_data.append([])
                self.table_data_tr = self.table_data[-1]

            self.row_num += 1
        elif tag == "td" or tag == "th":
            self.in_td = True
            self.rowspan = 1
            self.colspan = 1
            for attr_tuple in attrs:
                if "rowspan" in attr_tuple:
                    self.rowspan = attr_tuple[-1]
                elif "colspan" in attr_tuple:
                    self.colspan = attr_tuple[-1]

            if self.rowspan > 1:
                if self.col_num == 0:
                    empty_list = (int(self.rowspan)-1) * [[]]
                    self.table_data.extend(empty_list)
            self.col_num += 1

    def handle_endtag(self, tag):
        if tag == "tr":
            self.col_num = 0

        if tag == "td" or tag == "th":
            self.in_td = False

    @staticmethod
    def get_pos(_list, val):

        try:
            return _list.index(val)
        except Exception:
            return -1

    def handle_data(self, data):
        # print self.get_starttag_text()
        # print data
        if not self.in_td:
            return
        if self.get_starttag_text() ==None:
            return
        if "<div>" in self.get_starttag_text() or "<table" in self.get_starttag_text():
            return
        try:
            pos = self.get_pos(self.table_data_tr, SWNA)
            if pos > -1:
                for i in range(int(self.colspan)):
                    None_pos = self.table_data_tr.index(SWNA)
                    self.table_data_tr.pop(None_pos)
                    self.table_data_tr.insert(None_pos, data)

                return
            # fisrt line
            for i in range(int(self.colspan)):
                # col loop
                for pos, row_data in enumerate(self.table_data[self.row_num - 1:]):
                    # rowspan > 1, first line apped data
                    if not pos:
                        row_data.insert(self.col_num - 1, data)
                        continue
                    # other lines
                    if int(self.rowspan) > 1:
                        row_data.insert(self.col_num - 1, data)
                    else:
                        row_data.insert(self.col_num - 1, SWNA)

                self.col_num += 1
        except AttributeError:
            return


class OpenFile:
    """
    open the file with encode
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.check_file()
        self.file_str = self.open_file()

    def check_file(self):
        """
        check the file is excel
        :return:
        """
        if self.file_path.endswith(".xls") or self.file_path.endswith(".xlsx"):
            return

        _error = os.path.basename(self.file_path) + "is not excel."

        raise Exception(_error)

    def open_file(self):

        file_obj = open(self.file_path, "rU")
        _str = file_obj.read()
        if "<table" not in _str:
            _error = os.path.basename(self.file_path) + " does not have table."
            raise Exception(_error)
        # get the file encoding
        _code = chardet.detect(_str)["encoding"]
#         print "detect-01:",chardet.detect(_str)
#         # detect-01: {'confidence': 0.99, 'language': '', 'encoding': 'utf-8'}
        _str = _str.decode(_code)

        # # for ReportWindApply data
        # _str = re.sub("<meta http-equiv='content-type' content='application/ms-excel; charset=utf-8'/>", "", _str)
        # _str = re.sub('<tr style="font-weight:bold; background-color: #888; text-align: center;">', "<tr>", _str)
        # _str = re.sub('<tr style="vnd.ms-excel.numberformat:@">', "<tr>", _str)
        # _str = re.sub('<td style="vnd.ms-excel.numberformat:@">', "<td>", _str)

        # del the return
        _str = re.sub("[\t|\n]", "", _str)
        # add empty val
        _str = re.sub("<td></td>", "<td>&nbsp;</td>", _str)
        # replace &
        _str = re.sub("&RSE", "/RSE", _str)
        _str = re.sub("&amp;RSE", "EMC/RSE", _str)
        _str = re.sub("&PM", "SW/PM", _str)
        _str = re.sub("&amp;PM", "SW/PM", _str)

        _str = re.sub("&lt", "<", _str)
        _str = re.sub("&gt", ">", _str)
        _str = re.sub("&amp", "/", _str)
        _str = re.sub("&quote", '"', _str)
        _str = re.sub("&apos", "'", _str)

        # replace the empty val
        _str = re.sub("&nbsp;", u" ", _str)
        return _str


class ExportTableData(OpenFile):

    def __init__(self, file_path):
        self.file_path = file_path
        OpenFile.__init__(self, file_path)
        self.table_data = self.split_data()

    def split_data(self, write_excel=False):
        parser = MyHTMLParser()

        parser.feed(self.file_str)
        table_data = parser.table_data

        if write_excel:
            _name = os.path.basename(self.file_path)
            _path = os.path.split(self.file_path)[0]
            os.chdir(_path)
#             print "_name:",_name
            wb = xlsxwriter.Workbook(_name + ".xlsx")
            ws = wb.add_worksheet("test")
            for row, row_data in enumerate(table_data):
                for col, d in enumerate(row_data):
                    ws.write(row, col, d)

        return table_data


if __name__ == '__main__':
    _path = r"E:\Always\!EERF\files"
    _path = r"E:\Always\!EERF\EERF"
    file_path_list = []
    for _ in os.walk(_path):
        file_list = _[-1]
        if file_list:
            root_path = _[0]
            for file_name in file_list:
                each_file_path = os.path.join(root_path, file_name)
                file_path_list.append(each_file_path)

    # for _ in file_path_list:
    #     print "-"*100
    #     print os.path.basename(_)
    #     ExportTableData(_)

    Emp_file_path = r"C:\Users\F1233084\Desktop\OralceData\EERF\EmpRelChangeInfo.xls"
    _obj = ExportTableData(Emp_file_path)

    # get new excel
#     print _obj.split_data(write_excel=True)
