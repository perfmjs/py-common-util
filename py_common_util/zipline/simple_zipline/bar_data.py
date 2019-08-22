# -*- coding: utf-8 -*-
import pandas as pd
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from py_common_util.common.common_utils import CommonUtils


class BarData(object):
    """bar数据，参考zipline._protocol.BarData"""
    @property
    def current_kline_date(self):
        return self._current_kline_date

    @property
    def cassandra_session(self):
        return self._cassandra_session

    @property
    def simple_cassandra_session(self):
        return self._simple_cassandra_session

    def __init__(self):
        self._current_kline_date = None   # e.g. "2019-07-24"
        self._simple_cassandra_session = None
        self._cassandra_session = None

    def do_init(self, stock_type, cassandra_host_port, cassandra_key_space):
        self._stock_type = stock_type  # e.g. 'HK', 'US'
        # init cassandra session
        def pandas_factory(colnames, rows):
            return pd.DataFrame(rows, columns=colnames)
        cassandra_host, cassandra_port = cassandra_host_port.split(":")
        cluster = Cluster([cassandra_host],
                          load_balancing_policy=DCAwareRoundRobinPolicy(local_dc="datacenter1"),
                          port=int(cassandra_port))
        self._simple_cassandra_session = cluster.connect(cassandra_key_space)  # 简单的连接模式
        self._cassandra_session = cluster.connect(cassandra_key_space)
        self._cassandra_session.default_fetch_size = 10000000  # needed for large queries, otherwise driver will do pagination. Default is 50000.
        self._cassandra_session.row_factory = pandas_factory

    def set_current_kline_date(self, current_kline_date):
        self._current_kline_date = current_kline_date

    def can_trade(self, security_code):
        """
        当前bar能否交易
        :param security_code: 交易标的 e.g. "00700.HK"
        :param kline_date: bar日期 e.g. "2019-07-24"
        :return:
        """
        return True

    def current(self, security_code_list):
        """
        获取当前bar的itemView信息，重试10次
        :param security_code_list, e.g. ["00700.HK","01800.HK]
        :param kline_date: bar日期 e.g. "2019-07-24"
        :return: bar_item e.g. {"security_code": "00700.HK", "close": 1.0, "kline_date": "2019-07-24"}
        """
        i = 0
        while i < 1:
            df = self._daily_bar_to_pandas(cassandra_session=self.simple_cassandra_session,
                                             security_code_list=security_code_list,
                                             kline_date=self.current_kline_date)
            if df.empty:
                i += 1
            else:
                return df
        return df

    def calc_lot_size(self, security_code):
        """一手股票的股数, 美股为1，A股为100，港股中每手的股数不同"""
        if ".HK" in security_code:
            return 100  # TODO 先hard code 100
        elif ".SZ" in security_code or ".SH" in security_code:
            return 100
        else:
            return 1

    def can_buy_lot(self, cash, lot_size, price:float, min_move, commision):
        """
        计算当前金额可以买多少股票
        假设条件：1）当前腾讯股价为100CNY/股，2）有最小买入单位“手”=100股
        此时已经确定的逻辑：腾讯一手价值10000CNY，最多能持有19手（19手价值190000CNY<20万CNY，20手价值200000CNY=20万CNY，但是因为有手续费，所以不能采纳），手续费标准为千一，实际为190CNY。
        则完成该仓位时，分配给腾讯的仓位应该为19手腾讯（股票）+（10000-190）CNY现金。
        :param cash: e.g. 20万
        :param lot_size: e.g. 100
        :param price: e.g. 100
        :param min_move: e.g. 0
        :param commision: e.g. 0.001
        :return:
        """
        return self._calc_trade_lot(cash / (price + min_move + commision), lot_size)

    def _calc_trade_lot(self, trade_lot:int, lot_size:int=1):
        """
        把计划交易的股数转成可以被手数整除的实际股数
        trade_lot: 计划交易的股数， 可以为float类型的值
        lot_size 1手多少股
        """
        # if trade_lot <= lot_size:  # 如果数量小于1手，就下1手的数量
        #     return lot_size
        if trade_lot <= lot_size:  # 如果数量小于1手，就下0手的数量
            return 0
        if trade_lot % lot_size == 0:  # 刚好整除就下trade_lot数量，否则向下取整
            return trade_lot
        else:
            return int(trade_lot / lot_size) * lot_size

    @CommonUtils.print_exec_time
    def _daily_bar_to_pandas(self, cassandra_session, security_code_list, kline_date) -> pd.DataFrame:
        """
        参考：Get a Pandas DataFrame from a Cassandra query  https://gist.github.com/gioper86/b08b72d77c4e0aefa0137fc3655488dd
        https://stackoverflow.com/questions/41247345/python-read-cassandra-data-into-pandas
        :return:
        """
        table_name = ''
        if self._stock_type == 'HK':
            table_name = 'nocode_quant_hk_screen_data'
        elif self._stock_type == 'US':
            table_name = 'nocode_quant_us_screen_data'
        security_code_list_str = "'" + "','".join(security_code_list) + "'"
        filter_sql = """
        select security_code, hfq_close as close 
        from {0} 
        where trade_date = {1}
        and security_code in ({2})
        """.format(table_name, "'" + kline_date + "'", security_code_list_str)
        # 手工调用cassandra to pandas
        rows = cassandra_session.execute(filter_sql)
        security_list = []
        close_list = []
        for row in rows:
            security_list.append(row[0])
            close_list.append(row[1])
        data = {
            'security_code': pd.Series(security_list),
            'close': pd.Series(close_list),
        }
        df = pd.DataFrame(data)
        return df