# -*- coding: utf-8 -*-


class TradeContext(object):
    """交易过程的上下文，保存中间变量值, 参考zipline.algorithm.TradingAlgorithm"""
    def __init__(self, *args, **kwargs):
        self.trade_calendar_list = []  # 交易日历执行计划
        self.current_bar_item_day_date = None  # K线当日的日期，如"2019-08-01"
        self.current_bar_item_kline_date = None  # 当前k线的日期，分钟K线如"2019-08-01 15:30" 日K如"2019-08-01"
        self.stock_type = ""  # 股票类型 HK: 港股，US: 美股
        self.backtest_setting = None  # 回测设置