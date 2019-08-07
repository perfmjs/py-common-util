# -*- coding: utf-8 -*-
from abc import abstractmethod, ABCMeta
from six import with_metaclass
# import quandl
import zipline as zl
import pandas as pd
import numpy as np
import sys
from logbook import Logger, StreamHandler, FileHandler
# from skydl.zipline.tushare_dataset import TushareDataset


class AbstractStrategy(with_metaclass(ABCMeta)):
    """
    zipline数据默认缓存在：~/.zipline/data/
    10 Minutes to pandas  https://pandas.pydata.org/pandas-docs/stable/getting_started/10min.html
    https://github.com/quantopian/zipline
    量化交易实践篇（1）——量化交易平台Quantopian介绍 https://www.jianshu.com/p/5925f4f13a84
    量化交易实践篇（2）—— Quantopian策略实现初体验  https://www.jianshu.com/p/5f7a8f53045d
    ===============
    fix issue: Can't run zipline backtest without treasury data
    https://github.com/quantopian/zipline/issues/2422
    https://github.com/nateGeorge/treasury_data_backup
    ...
    data['SPY'].to_csv('~/.zipline/data/treasury_curves.csv')  # 手工生成treasury_curves.csv文件
    ...
    ===============
    ```
    参考：https://github.com/quantopian/zipline/blob/master/zipline/examples/dual_moving_average.py
    https://www.google.com/search?q=zipline+multiple+stocks&rlz=1C5CHFA_enCN643CN643&oq=zipline+multiple+stocks&aqs=chrome..69i57.809j0j9&sourceid=chrome&ie=UTF-8
    https://groups.google.com/forum/#!topic/zipline/1GFJSyRwd7w
    https://www.quantopian.com/posts/applying-strategy-to-multiple-stocks-fail
    http://quantfiction.com/2018/08/20/trading-metrics-that-actually-matter/
    https://github.com/rainx/inside-zipline/blob/master/tradingcalendar/tc.md
    backtrader实战和工程师思维的选型 http://www.topquant.vip/?p=766
    https://www.yiibai.com/pandas/python_pandas_statistical_functions.html
    https://github.com/gbeced/pyalgotrade
    https://www.zhihu.com/question/30719154
    https://www.e-learn.cn/en/node/2160872
    https://0xboz.github.io/blog/how-to-create-custom-zipline-bundles-from-binance-data-part-1/
    https://0xboz.github.io/blog/how-to-create-custom-zipline-bundles-from-binance-data-part-2/
    https://github.com/quantopian/empyrical
    https://github.com/quantopian/pyfolio
    https://github.com/quantopian/alphalens
    pyfolio教程2——第一个returns_tear_sheet  https://blog.csdn.net/qtlyx/article/details/88724236
    https://github.com/marketneutral/alphatools/blob/master/notebooks/research-minimal.ipynb
    http://pmorissette.github.io/ffn/quick.html
    https://www.quantopian.com/posts/does-order-target-sid-0-close-a-short-position
    关于QP的量化三大件：pyFolio，zipline，alphalens：TopQ极宽backtrader课件系列  http://www.topquant.vip/?p=854
    深入了解zipline回测框架 https://github.com/rainx/inside-zipline
    1.5 量化技术篇—使用zipline回测  https://www.jianshu.com/p/b6c826300c6e
    zipline 因子和策略开发代码集 http://www.trader-china.cn/topics/55154
    AI For Trading:Zipline Pipeline (50)  http://www.digtime.cn/articles/131/ai-for-tradingzipline-pipeline50
    ```
    """
    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, value):
        self._log = value

    # @property
    # def ts(self):
    #     return self._ts

    @property
    def zipline(self):
        return self._zipline

    @property
    def pandas(self):
        return self._pd

    @property
    def numpy(self):
        return self._np

    def __init__(self):
        """
        Python日志记录包logbook https://blog.yasking.org/a/python-logbook.html
        记录日志到文件和STDOUT
        使用StreamHandler记录的日志会以流输出，这里指定sys.stdout也就是记录到标准输出，与print一样
        StreamHandler(sys.stdout, level='DEBUG').push_application()
        FileHandler('app.log', bubble=True, level='INFO').push_application()
        """
        StreamHandler(sys.stdout).push_application()
        self._log = Logger(self.__class__.__name__)
        # quandl.ApiConfig.api_key = ""  # 不可向外泄露api_key
        # self.log.info("quandl version: " + quandl.version.VERSION)
        # self._ts = TushareDataset(log=self._log)
        self._zipline = zl
        self.log.info("zipline version: " + self.zipline.__version__)
        self._pd = pd
        self.log.info("pandas version: " + self.pandas.__version__)
        self._np = np
        self.log.info("numpy version: " + self.numpy.__version__)

    @abstractmethod
    def prepare_data(self):
        # zipline数据默认缓存在：~/.zipline/data/
        return None

    @abstractmethod
    def initialize(self, context):
        # 启动后需要用户干预处理的一次性逻辑
        self.log.info("initialize...")

    @abstractmethod
    def before_trading_start(self, context, data):
        # 每个bar_open之前执行，对日K可选定当天待交易股票，分钟K在每日盘前可以用于初始化数据
        # self.log.info("before_trading_start...")
        pass

    @abstractmethod
    def handle_data(self, context, data):
        # 定时执行，处理当前周期中待处理订单
        # self.log.info("handle_data...")
        pass

    @abstractmethod
    def analyze(self, context, records):
        self.log.info("analyze...")

    @abstractmethod
    def run_algorithm(self):
        """
        调用例子：
        start_time = self.pandas.Timestamp('2018-01-02 09:31:00', tz='utc')
        end_time = self.pandas.Timestamp('2018-02-04 16:00:00', tz='utc')
        data_frequency = 'minute'
        perf = zipline.run_algorithm(start=start_time,
                             end=end_time,
                             initialize=self.initialize,
                             capital_base=100000,
                             handle_data=self.handle_data,
                             before_trading_start=self.before_trading_start,
                             data_frequency=data_frequency,
                             data=self.prepare_data(),
                             trading_calendar=ChineseStockCalendar(data_frequency=data_frequency),
                             analyze=self.analyze)
        return perf
        """
        self.log.info("run_algorithm...")
        return None


if __name__ == '__main__':
    AbstractStrategy().run_algorithm()
