# -*- coding: utf-8 -*-


class BacktestSetting(object):
    """回测的基本设置"""
    def __init__(self, trade_mode, start_date, end_date, benchmark_code, init_amount:int=1000000, cost:float=0.001):
        self.trade_mode_type = 0  # 目前只有0:定期轮动，回测类型 0:定期轮动，下标从0开始
        self.trade_mode = trade_mode  # 交易模型：0: 定期轮动
        self.start_date = start_date[0:4]+"-"+start_date[4:6]+"-"+start_date[6:8]  # 起始日期 e.g. "2019-01-01"
        self.end_date = end_date[0:4]+"-"+end_date[4:6]+"-"+end_date[6:8]  # 结束日期 e.g. "2019-01-01"
        self.init_amount = int(init_amount)  # 初始金额(元)
        self.benchmark_code = benchmark_code  # 指数作为基准标的
        self.cost = float(cost)  # 手续费  0:零, 0.001: 千分之一, 0.002:千分之2, 0.005:千分之五, 0.01:千分之十

