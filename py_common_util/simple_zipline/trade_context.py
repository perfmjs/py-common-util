# -*- coding: utf-8 -*-


class TradeContext(object):
    """交易过程的上下文，保存中间变量值, 参考zipline.algorithm.TradingAlgorithm"""
    def __init__(self, *args, **kwargs):
        self.trade_calendar_list = []  # 交易日历执行计划
        self.current_bar_item_day_date = None  # K线当日的日期，如"2019-08-01"
        self.current_bar_item_kline_date = None  # 当前k线的日期，分钟K线如"2019-08-01 15:30" 日K如"2019-08-01"
        self.stock_type = ""  # 股票类型 HK: 港股，US: 美股
        self.backtest_setting = None  # 回测设置
        self.use_real_price = True  # 是否使用动态复权逻辑回测，True->以不复权的真实价建仓，以动态复权价刷新持仓市值 False->以后复权价格建仓和刷新持仓市值



