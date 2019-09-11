# -*- coding: utf-8 -*-
from abc import abstractmethod, ABCMeta
import pandas as pd
import sys
import traceback
import random
from py_common_util.common.common_utils import CommonUtils
from py_common_util.zipline.simple_zipline.trade_order import TradeOrder
from py_common_util.zipline.simple_zipline.bar_data import BarData
from py_common_util.common.enhanced_ordered_dict import EnhancedOrderedDict
from py_common_util.zipline.simple_zipline.trade_context import TradeContext
from six import with_metaclass
from logbook import Logger, StreamHandler, FileHandler


class SimpleAbstractStrategy(with_metaclass(ABCMeta)):
    """
    简单的策略回测抽象，参考了zipline的设计思路
    https://github.com/quantopian/zipline/blob/7056a9091423d1465968d21498b18de75ba7c6c6/zipline/finance/metrics/metric.py
    https://github.com/quantopian/zipline/blob/7e642c8e7ef49b2250d47074ce3295a39bb0726d/zipline/finance/ledger.py
    https://github.com/quantopian/zipline/blob/3106d495f0521639b4be6a77f35c194e849e6c1f/zipline/data/benchmarks.py
    """
    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, value):
        self._log = value

    @property
    def trade_context(self):
        return self._trade_context

    @property
    def bar_data(self):
        return self._bar_data

    @property
    def records(self):
        return self._records

    @property
    def trade_order(self):
        return self._trade_order

    @property
    def multiple_order_position_dict(self):
        return self._multiple_order_position_dict

    @property
    def perf(self):
        return self._perf

    @property
    def sink_fn(self):
        return self._sink_fn

    @property
    def sink_out_dict(self):
        return self._sink_out_dict

    def __init__(self):
        StreamHandler(sys.stdout).push_application()
        self._log = Logger(self.__class__.__name__)
        self._perf = pd.DataFrame()
        self._records = EnhancedOrderedDict()
        self._trade_context = TradeContext()
        self._sink_fn = self.sink
        self._sink_out_dict = EnhancedOrderedDict()
        # build bar_data
        self._bar_data = BarData()
        # build trade order
        self._trade_order = TradeOrder()
        # build multiple order position dict
        self._multiple_order_position_dict = EnhancedOrderedDict()

    def add_sink_fn(self, sink_fn):
        """
        增加sink方法，支持分布式远程执行sink
        :param sink_fn: sink方法
        :return:
        """
        self._sink_fn = sink_fn
        return self

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

    def sink(self, value: EnhancedOrderedDict):
        """持久化输出对象"""
        pass

    def run_algorithm(self):
        try:
            self.prepare_data()
            self.initialize(self.trade_context)
            for trade_date in self.trade_context.trade_calendar_list:
                self.trade_context.current_bar_item_day_date = trade_date
                self.trade_context.current_bar_item_kline_date = trade_date
                self.bar_data.set_current_kline_date(trade_date)
                self.before_trading_start(context=self.trade_context, data=self.bar_data)
                self.handle_data(context=self.trade_context, data=self.bar_data)
            self.analyze(context=self.trade_context, records=self.records)
            self.sink_fn(self.sink_out_dict)
            return self.perf
        except Exception as e:
            self.log.error("error occurred while backtesting: %s" % str(e))
            traceback.print_exc()
        return None

    @CommonUtils.print_exec_time
    def process(self):
        return self.run_algorithm()

    def _draw_return_rate_line(self, perf):
        """"画图，可以用于开发调试"""
        import seaborn as sns
        import matplotlib.pyplot as plt
        from matplotlib.dates import DateFormatter
        from pandas.plotting import register_matplotlib_converters
        register_matplotlib_converters()
        sns.set_style('darkgrid')
        sns.set_context('notebook')
        ax = plt.axes()
        # # 设置时间显示格式
        years_fmt = DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(years_fmt)
        # 让x轴坐标旋转45度
        labels = ax.get_xticklabels()
        plt.setp(labels, rotation=35, horizontalalignment='right')
        # 画出收益率曲线
        sns.lineplot(x='period_close',
                     y='strategy_return',
                     data=perf,
                     label="strategy_return")
        sns.lineplot(x='period_close',
                     y='benchmark_return',
                     data=perf, label="benchmark_return")
        plt.legend(loc='upper left')
        plt.title("return rate of strategy and benchmark")
        plt.xlabel('time')
        plt.ylabel('return rate')
        plt.show()
        # # save plt
        # fig = ax.get_figure()
        # fig.savefig('～/gender_salary.png')

    @staticmethod
    def _random_subset(list, select_num=10, random_seed=10, head_start=0, head_end=2, foot_start=-2, foot_end=None):
        """
        保留头尾各n个元素，其它元素从list中间元素中随机选择指定数量的元素
        :param list: 目标list e.g. list = [i for i in range(189)]
        :param select_num: 指定输出元素数量（包括头尾元素）
        :param random_seed 随机种子，在random_seed相同的情况下返回结果是固定的
        :param head_start 保留前面部分的第head_start到head_end之间的元素，不包含index为head_end的元素
        :param head_end 同head_start
        :param foot_start 保留后面面部分的第foot_start到foot_end之间的元素，不包含index为head_end的元素(foot_end=None除外)
        :param foot_end 为None表示包含最后一个元素
        :return: 选定后的list e.g. _random_subset([3], 10)->[3], _random_subset(list, 10)->[0, 1, 5, 10, 111, 125, 148, 149, 187, 188]
        """
        head_list = list[head_start:head_end]
        foot_list = list[foot_start:foot_end]
        default_element_num = len(head_list) + len(foot_list)
        if list is None or select_num < default_element_num or len(list) <= select_num:
            return list
        indexs = [i for i in range(len(list))]
        mid_list = indexs[head_end:foot_start]
        random.seed(random_seed)
        slice_indexs = random.sample(mid_list, select_num - default_element_num)
        slice_indexs = sorted(slice_indexs, key=int, reverse=False)
        return head_list + [list[i] for i in slice_indexs] + foot_list


if __name__ == '__main__':
    SimpleAbstractStrategy().process()
