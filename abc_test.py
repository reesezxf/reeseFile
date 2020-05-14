# encoding:utf-8
"""
@Create Time: 2020/3/17 上午 09:40
@Author: F1233225
@Description:
"""
import os
import xlsxwriter
import objgraph
import tracemalloc
from summary import Summary, WriteSheet
import csv
import numpy as np
from sys import getsizeof


def get_all_files(path):
    all_files = []
    for root, dirs, files in os.walk(path):
        for name in files:
            # print(os.path.join(root, name))
            all_files.append(os.path.join(root, name))
    # print(all_files)
    return all_files


def write_sheet():
    workbook = xlsxwriter.Workbook(r'D:\PySpace\FATPWipasDataAnalysisReport\test_write.xlsx')
    sheet = workbook.add_worksheet('test')
    sheet.hide_gridlines(2)
    data = [['a', 'li', 20], ['a', 'wang', 22], ['a', 'max', 23]]
    for i, d in enumerate(data):
        for j, v in enumerate(d):
            sheet.write(i, j, v)
    workbook.close()


def hidden_test():
    workbook = xlsxwriter.Workbook('test_hidden.xlsx')
    worksheet = workbook.add_worksheet('SENSORS')

    workbook.get_worksheet_by_name('SENSORS').set_column(5, 7, None, None, {'hidden': 1})

    for col_num in range(8):
        worksheet.write(0, col_num, col_num)

    workbook.close()


def run_summary():
    kw_pat = r'D:\PySpace\FATPWipasDataAnalysisReport\testdata\WiPAS data analysis Keyword.xlsx'
    report_pat = r'D:\PySpace\FATPWipasDataAnalysisReport\testdata\bbb'
    tracemalloc.start(25)
    file_list = get_all_files(report_pat)
    s = Summary(kw_pat, file_list)

    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('traceback')
    print(tracemalloc.get_traced_memory())
    stat = top_stats[0]
    print("%s memory blocks: %.1f KiB" % (stat.count, stat.size / 1024))
    for line in stat.traceback.format():
        print(line)
    # for stat in top_stats[:10]:
    #     print(stat)
    objgraph.show_most_common_types(5)

    WriteSheet(s.yield_summary_data, s.fail_item_data, s.fail_info_data, s.retest_item_data, s.retest_info_data)


def get_csv_data(csv_file):
    """get csv data"""
    csv_data = []
    with open(csv_file, 'r') as f:
        csv_reader = csv.reader(f)
        for row_data in csv_reader:
            csv_data.append(row_data)
    return csv_data


def get_nparray_size():
    p = r'D:\PySpace\FATPWipasDataAnalysisReport\testdata\bbb\Ether Scorpio.csv'
    csv_data = get_csv_data(p)
    print('origin size:', getsizeof(csv_data))
    np_data = np.array(csv_data)

    print('np array size:', np_data.nbytes)


if __name__ == '__main__':
    # get_all_files(report_path)
    # write_sheet()
    # hidden_test()
    # run_summary()
    get_nparray_size()
