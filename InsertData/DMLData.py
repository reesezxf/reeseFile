# coding:utf-8
"""
@author: Sara
"""

from generalParametes import GeneralParameters

import cx_Oracle
import time
import os

# 针对 Oracle 与 Python 编码不一致
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.AL32UTF8'


class oracle:
    def __init__(self):
        """
        # 初始化
        """
        self.db = None
        self.connect()

    def connect(self):
        """
        @note: connect oracle
        """
        print 'connect oracle .....'
        try:
            # 通过 username，password，oracle_path 来连接 cx_Oracle
            self.db = cx_Oracle.Connection(GeneralParameters.username, GeneralParameters.password,
                                           GeneralParameters.oracle_path)
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            if error.code == 1017:
                print('Please check your credentials.')
            else:
                print('Database connection error: %s'.format(e))
            raise

    def disConnect(self):
        """
        @note: disconnect oracle
        """
        print 'disconnect oracle .....'
        try:
            # 断开与cx_Oracle的连接
            self.db.close()
        except cx_Oracle.DatabaseError:
            pass

    def selectData(self, col_string, table_name, where_string=''):
        """
        @note: select data from table
        @return: [(data1), (data2), (data3), (data4)]
        """
        cur = self.db.cursor()
        # 降序:desc; 升序:asc
        # 组成 SQL 语句
        sql_string = 'select ' + col_string + ' from ' + table_name
        if where_string:
            sql_string = sql_string + ' where ' + where_string
            # print('sql:', sql_string)
        try:
            # 游标 执行 sql_string 语句
            cur.execute(sql_string)
            # 获取 查询的结果
            res = cur.fetchall()
        except Exception, e:
            raise Exception(e)
        finally:
            # 关闭游标
            cur.close()

        return res

    def selectFK(self, col_string, table_name, where_string=''):
        """
        @note: select data from table
        @return: [(data1), (data2), (data3), (data4)]
        """
        cur = self.db.cursor()
        # 组成 SQL 语句
        sql_string = 'select ' + col_string + ' from ' + table_name
        if where_string:
            sql_string = sql_string + ' where ' + where_string
        try:
            # 游标 执行 sql_string 语句
            cur.execute(sql_string)
            # 获取 查询的结果
            res = cur.fetchone()
        except Exception, e:
            raise Exception(e)
        finally:
            # 关闭游标
            cur.close()

        return res

    def selectColumns(self, table_name):
        """
        @note: select data from table
        @return: [(data1), (data2), (data3), (data4)]
        """
        table_name = table_name.upper()
        cur = self.db.cursor()
        # 组成 SQL 语句
        sql_string = 'select COLUMN_NAME from user_tab_columns where table_name ' + "in ('" + table_name + "')"
        try:
            # 游标 执行 sql_string 语句
            cur.execute(sql_string)
            # 获取 查询的结果
            columns_name = cur.fetchall()
        except Exception, e:
            raise Exception(e)
        finally:
            # 关闭游标
            cur.close()

        return columns_name

    def insertData(self, data, col_string, table_name):
        """
        @note: insert data into oracle
        """
        start_time = time.clock()
        select_cursor = self.db.cursor()
        # 组成 SQL 语句
        select_sql_string = 'select ' + col_string + ' from ' + table_name
        select_cursor.execute(select_sql_string)
        db_types = [d[1] for d in select_cursor.description]

        cursor = self.db.cursor()
        cursor.bindarraysize = len(data)
        cursor.setinputsizes(*db_types)
        value_num_sting = self.getValueNumString(len(db_types))
        # 组成 SQL 语句
        sql_string = 'insert into ' + table_name + ' (' + col_string + ' ) values ( ' + value_num_sting + ' )'
        try:
            # 游标 执行 sql_string 语句（executemany 批量插入）
            cursor.executemany(sql_string, data)
            # 提交事务
            self.db.commit()
            end_time = time.clock()
            print '-------------', table_name, '结束连接数据库咯---------- 耗时:', end_time - start_time
        except cx_Oracle.DatabaseError as msg:
            print "insertData DatabaseError msg:", msg
            raise
        finally:
            # 关闭游标
            cursor.close()

    def emptyTable(self, table):
        """
        @note: empty tables
        """
        cursor = self.db.cursor()
        del_sql = 'delete from ' + table
        # 游标 执行 del_sql 语句
        cursor.execute(del_sql)
        # 提交事务
        self.db.commit()

    def deleteData(self, table_name, where_string):
        """
        @note: delete data from tables
        """
        cursor = self.db.cursor()
        try:
            del_sql = 'delete from ' + table_name + ' where ' + where_string
            # print(del_sql)
            cursor.execute(del_sql)
            self.db.commit()
            print('deleteData  ：    Delete compeled      ')
        except cx_Oracle.DatabaseError as msg:
            print ("insertData DatabaseError msg:", msg)
            raise
        finally:
            cursor.close()

    def updateData(self, sql_string):
        """
        @note: update data into oracle
        """
        start_time = time.clock()
        cursor = self.db.cursor()
        try:
            # 游标 执行 sql_string 语句
            cursor.execute(sql_string)
            # 提交事务
            self.db.commit()
            end_time = time.clock()
            print '--updateData', '结束连接数据库咯---------- 耗时:', end_time - start_time
        except cx_Oracle.DatabaseError as msg:
            print "updateData DatabaseError msg:", msg
            raise
        finally:
            # 关闭游标
            cursor.close()

    @staticmethod
    def getValueNumString(value_num):
        """
        @note:
        @return :1, :2, :3, :4, :5, :6, :7, :8, :9, :10
        """
        value_num_sting = ''

        for num in range(1, value_num + 1):
            str_num = str(num)
            str_num = ':' + str_num
            if num == 1:
                value_num_sting = str_num
            else:
                value_num_sting = value_num_sting + ', ' + str_num

        return value_num_sting
