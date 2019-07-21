# coding: utf-8 or # -*- coding: utf-8 -*-
import pandas as pd
from py_common_util.tushare import MySQLUtils


class PandasUtils(object):

    def __init__(self):
        self._mysql_util = MySQLUtils()
        pass

    def read_sql(self, select_sql):
        return pd.read_sql(select_sql, self._mysql_util.engine)


if __name__ == '__main__':
    pandas = PandasUtils()
    df = pandas.read_sql("SELECT code FROM tushare_2017.stock_basics")
    for code in df.code.values:
        print(code)
