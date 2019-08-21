# -*- coding: utf-8 -*-
import uuid
from py_common_util.common.enhanced_ordered_dict import EnhancedOrderedDict


class MultipleOrderPosition(object):
    """
    多个标的每日轮动回测类型的订单，参考：https://github.com/quantopian/zipline/blob/master/zipline/finance/order.py
    每个调仓周期只对应1个MultipleOrderPosition对象，而每个MultipleOrderPosition对象对应有调仓周期中所有日期的持仓字典position_dict
    init_cash: 回测时的初始总金额。后面会浮动变成total_value
    total_profit 多只股票的总收益 (会根据最新价浮动变化，每笔交易中多只股票里累计每只股票的股数*price，不计算手续费和min_move)
    total_balance_cash 剩余的总现金 (不会根据最新价浮动变化，本金减去了每笔历史交易当时的total_profit、手续费、min_move，之后还剩余的现金)
    total_value  每日策略内多只股票累加的总价值=total_profit+total_balance_cash
    turnover_ratio 调仓换手率：每次调仓期初换股当日的换手率(TODO 全被换为1，没有换股则为0，第1天交易为0)。计算公式：调仓换股后的上期末总价值中被减仓部分的价值之和 / 这次调仓换股前的上期末的总价值，其中总价值=sum(每只股票的last_price*持仓股数)
    """
    @property
    def position_dict(self):
        return self._position_dict

    def __init__(self, start_date, init_cash, id=None):
        self.id = self._make_id() if id is None else id
        self.start_date = start_date  # 格式如："2019-01-01"
        self.end_date = ""
        self.total_profit = 0.0
        self.total_balance_cash = init_cash
        self.total_value = init_cash
        self._position_dict = EnhancedOrderedDict()  # 每日日期-> trade_order.position_dict.copy()
        self.turnover_ratio = 0.0

    def set_end_date(self, end_date):
        """更新该调仓周期的结束日期"""
        self.end_date = end_date

    def set_adjust_turnover_ratio(self, turnover_ratio):
        """在新的调仓日期调仓完毕后更新该调仓周期的调仓换手率"""
        self.turnover_ratio = turnover_ratio

    def get_last_day_position_dict(self):
        """
        使用：[security_code for security_code in get_last_day_position_dict()[1].keys()]
        :return 返回tuple: (trade_date, security_position_dict)
        """
        if len(self.position_dict) > 0:
            return self.position_dict.to_list()[-1]
        else:
            return None

    def update(self, trade_date, position_dict_copy):
        # 更新每天的持仓明细
        self.position_dict[trade_date] = position_dict_copy
        # curr_batch_total_income = 0
        # curr_batch_total_profit = 0
        # curr_batch_total_balance_cash = 0
        # curr_batch_total_value = 0
        # for security_code in self.position_dict[trade_date]:
        #     position = self.position_dict[trade_date].get(security_code)
        #     curr_batch_total_income += position.income
        #     curr_batch_total_profit += position.amount * position.last_price
        #     curr_batch_total_balance_cash += position.balance_cash
        #     curr_batch_total_value += curr_batch_total_profit + curr_batch_total_balance_cash
        # self.total_profit += curr_batch_total_profit  # TODO 应该同一批次的多个日期一起计算
        # self.total_value += curr_batch_total_value  # TODO 应该同一批次的多个日期一起计算
        # print(trade_date + ", MultipleOrderPosition#curr_batch_total_value=" + str(curr_batch_total_value))

    @staticmethod
    def _make_id():
        return uuid.uuid4().hex

    def to_dict(self):
        """
        Creates a dictionary representing the state of this position.
        Returns a dict object of the form:
        """
        position_dict_str = ""
        for trade_date in self.position_dict:
            position_dict_str += trade_date + ":"
            for security_code in self.position_dict.get(trade_date):
                position_dict_str += str(self.position_dict.get(trade_date).get(security_code).to_dict()) + ","
        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'total_balance_cash': self.total_balance_cash,
            "total_profit": self.total_profit,
            "total_value": self.total_value,
            "position_dict": position_dict_str
        }
