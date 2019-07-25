# -*- coding: utf-8 -*-
from datetime import time, datetime
from trading_calendars import TradingCalendar
from zipline.utils.memoize import lazyval
from pandas.tseries.offsets import CustomBusinessDay
import pytz
from pytz import timezone


class ChineseStockCalendar(TradingCalendar):
    """
    for creating and registering our calendar
    Exchange calendar for 24/7 trading.
    Open Time: 12am, UTC
    Close Time: 11:59pm, UTC
    参考：https://github.com/zhanghan1990/zipline-chinese/blob/master/zipline/utils/tradingcalendar_china.py
    """
    @property
    def data_frequency(self):
        return self._data_frequency

    def __init__(self, data_frequency='minute'):
        self._data_frequency = data_frequency  # 'minute' or 'daily'
        super().__init__()

    @property
    def name(self):
        return "chinese_stock_calendar"

    @property
    def tz(self):
        return timezone("UTC")

    @property
    def open_times(self):
        return [(None, time(9, 31))] if self.data_frequency == 'minute' else [(None, time(0))]

    @property
    def close_times(self):
        return [(None, time(16))] if self.data_frequency == 'minute' else [(None, time(0))]

    @lazyval
    def day(self):
        return CustomBusinessDay(
            holidays=self.adhoc_holidays,
            weekmask='Mon Tue Wed Thu Fri',  # Mon Tue Wed Thu Fri Sat Sun
        )

    @property
    def adhoc_holidays(self):
        return [datetime(2018, 1, 15, tzinfo=pytz.utc)]
