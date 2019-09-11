# -*- coding: utf-8 -*-
import uuid
from py_common_util.common.enhanced_ordered_dict import EnhancedOrderedDict


class MultipleOrderPosition(object):
    """
    多个标的每日轮动回测类型的订单，参考：https://github.com/quantopian/zipline/blob/master/zipline/finance/order.py
    每个调仓周期只对应1个MultipleOrderPosition对象，而每个MultipleOrderPosition对象对应有调仓周期中所有日期的持仓字典position_dict
    init_cash: 回测时的初始总金额。后面会浮动变成total_value
    total_profit 多只股票的总收益 (会根据最新价浮动变化，每笔交易中多只股票里累计每只股票的股数*price，不计算手续费和min_move)
    total_balance_cash 【start_date调仓后 至 end_date日准备进行下个调仓周期前的持仓】剩余的总现金 (不会根据最新价浮动变化，本金减去了每笔历史交易当时的total_profit、手续费、min_move，之后还剩余的现金)
    total_value  每日策略内多只股票累加的总价值=total_profit+total_balance_cash
    turnover_ratio 调仓换手率。调仓日换手率计算公式:（每次调仓日卖出的股票市值+每次调仓日买入的股票市值 * 0.5 / (调仓后）账户总资产
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
        self.turnover_adjust_total_value = 0.0  # 每次调仓时卖出和调整过的股票市值
        self.turnover_ratio = 0.0  # 调仓换手率（内部计算）
        self.rebalance_count = 0  # 调仓换股次数：调仓日计算每只股票的换股次数总和，只要是卖出股票的交易都计算为1次换股

    def set_end_date(self, end_date):
        """更新该调仓周期的结束日期"""
        self.end_date = end_date

    def set_turnover_adjust_total_value(self, turnover_adjust_total_value):
        """在新的调仓日期调仓完毕后更新该调仓周期的调仓换手率之计算分子：每次调仓时卖出和调整过的股票市值"""
        self.turnover_adjust_total_value = turnover_adjust_total_value

    def set_rebalance_count(self, rebalance_count):
        """在新的调仓日期调仓完毕后更新该调仓周期的调仓换股次数"""
        self.rebalance_count = rebalance_count

    def get_last_day_position_dict(self):
        """
        使用：[security_code for security_code in get_last_day_position_dict()[1].keys()]
        :return 返回tuple: (trade_date, security_position_dict)
        """
        if len(self.position_dict) > 0:
            return self.position_dict.to_list()[-1]
        else:
            return None

    def update(self, trade_date, position_dict_copy, total_balance_cash):
        # 更新每天的持仓明细
        self.position_dict[trade_date] = position_dict_copy
        self.total_balance_cash = total_balance_cash
        total_profit = 0
        should_del_security_list = []
        for security_code in self.position_dict[trade_date]:
            position = self.position_dict[trade_date].get(security_code)
            if position.amount > 0:
                total_profit += position.amount * position.last_price
                self.total_balance_cash += position.balance_cash
            else:
                should_del_security_list.append(security_code)
        # 删除amount=0的已经卖空了的持仓
        for security_code in should_del_security_list:
            del self.position_dict[trade_date][security_code]
        self.total_profit = total_profit
        self.total_value = self.total_profit + self.total_balance_cash
        # 计算每个调仓日的换手率
        if self.start_date == trade_date and self.total_value > 0:
            self.turnover_ratio = self.turnover_adjust_total_value * 0.5 / self.total_value

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
            "turnover_adjust_total_value": self.turnover_adjust_total_value,
            "turnover_ratio": self.turnover_ratio,
            "position_dict": position_dict_str
        }
