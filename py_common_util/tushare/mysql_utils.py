# coding: utf-8 or # -*- coding: utf-8 -*-
from sqlalchemy import create_engine
"""
解决MYSQL更新数据Error Code: 1175. You are using safe update
SET SQL_SAFE_UPDATES = 0; 降低数据库修改模式
SET SQL_SAFE_UPDATES = 1; 提高数据库修改模式
"""


class MySQLUtils(object):

    @property
    def engine(self):
        return self._engine

    def __init__(self):
        self._engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/tushare_2017?charset=utf8')

    def append_data(self, df, table_name):
        # 追加数据到现有表
        df.to_sql(table_name, self.engine, if_exists='append')

    def replace_data(self, df, table_name):
        # 覆盖数据到现有表
        df.to_sql(table_name, self.engine, if_exists='replace')

    def insert_data_safely(self, df, table_name):
        # 如果表存在就报错
        df.to_sql(table_name, self.engine, if_exists='fail')


if __name__ == '__main__':
    mysqlUtil = MySQLUtils()
    import pandas as pd
    df = pd.read_sql("SELECT * FROM tushare_2017.stock_basics", mysqlUtil.engine)
    print(df)
