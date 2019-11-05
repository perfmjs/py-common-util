# -*- coding: utf-8 -*-


class RegularRotationTradeMode(object):
    """定期轮动回测交易模式"""
    def __init__(self, rebalance_cycle:int=1, max_holding_count:int=10, buy_way:int=0):
        self.rebalance_cycle = int(rebalance_cycle)   # 调仓日期, 如: 5, 即第1天，第6天，第11天，。。。
        self.max_holding_count = int(max_holding_count)  # 最大持仓股票个数
        self.buy_way = int(buy_way)  # 买入方式 0:等权重，下标从0开始