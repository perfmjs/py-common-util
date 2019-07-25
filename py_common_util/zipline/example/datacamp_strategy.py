# -*- coding: utf-8 -*-
from contrib.quant.zipline.default_strategy import DefaultStrategy
from contrib.quant.utils.chinese_stock_calendar import ChineseStockCalendar
import datetime


class DataCampStrategy(DefaultStrategy):
    """
    Python for Finance Tutorial For Beginners
    https://github.com/datacamp/datacamp-community-tutorials/blob/master/Python%20Finance%20Tutorial%20For%20Beginners/Python%20For%20Finance%20Beginners%20Tutorial.ipynb
    """
    def __init__(self):
        super().__init__()

    def prepare_data(self):
        from collections import OrderedDict
        data = OrderedDict()
        from pandas_datareader import data as pdr
        data['SPY'] = pdr.get_data_yahoo('AAPL',
                                  start=datetime.datetime(2018, 1, 2),
                                  end=datetime.datetime(2018, 5, 10))
        data['SPY'].to_csv('~/.zipline/data/treasury_curves.csv')  # 手工生成treasury_curves.csv文件
        data['SPY'] = data['SPY'][['Open', 'High', 'Low', 'Close', 'Volume']]
        panel = self.pandas.Panel(data)
        panel.major_axis = panel.major_axis.tz_localize(tz='utc')
        panel.minor_axis = ['open', 'high', 'low', 'close', 'volume']
        return panel

    def initialize(self, context):
        super().initialize(context)
        context.sym = self.zipline.api.symbol('SPY')
        print("22222", context.sym)

    def before_trading_start(self, context, data):
        super().before_trading_start(context, data)

    def handle_data(self, context, data):
        super().handle_data(context, data)

    def analyze(self, context, records):
        super().analyze(context, records)

    def run_algorithm(self):
        start_time = self.pandas.Timestamp('2018-01-02 00:00:00', tz='utc')
        end_time = self.pandas.Timestamp('2018-05-10 00:00:00', tz='utc')
        data_frequency = 'daily'
        perf = self.zipline.run_algorithm(start=start_time,
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


if __name__ == '__main__':
    DataCampStrategy().run_algorithm()

