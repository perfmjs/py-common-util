# -*- coding: utf-8 -*-
from abc import abstractmethod, ABCMeta
from six import with_metaclass
import sys
from logbook import Logger, StreamHandler, FileHandler


class SimpleAbstractStrategy(with_metaclass(ABCMeta)):
    """
    简单的策略抽象，参考了zipline的设计思路
    """
    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, value):
        self._log = value

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
    SimpleAbstractStrategy().run_algorithm()
