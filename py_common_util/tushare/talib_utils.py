# -*- coding:utf-8 -*-
import talib
from py_common_util.tushare import PandasUtils
from py_common_util.tushare import MySQLUtils
'''
量化工具TA-Lib 使用例子 http://30daydo.com/article/196
'''


class TalibUtils(object):

    @property
    def version(self):
        return 'tushare_2017'

    def __init__(self):
        print("TA-lib -v: " + talib.__version__)


if __name__ == '__main__':
    talib_util = TalibUtils()
    # talib_util.MA(df.close.values, timeperiod=5, matype=0)