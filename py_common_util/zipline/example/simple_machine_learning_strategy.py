# -*- coding: utf-8 -*-
import pandas as pd
from zipline.api import order_target_percent, record, symbol
import pytz
import zipline
from datetime import datetime
from contrib_lib.quant.utils.chinese_stock_calendar import ChineseStockCalendar
# Use a random forest classifier. More here: http://scikit-learn.org/stable/user_guide.html
from sklearn.ensemble import RandomForestClassifier
from collections import deque
import numpy as np
from collections import OrderedDict
from contrib_lib.quant.zipline.default_strategy import DefaultStrategy


class SimpleMachineLearningStrategy(DefaultStrategy):
    """
    机器学习算法交易
    参考：https://www.quantopian.com/posts/simple-machine-learning-example
    进化策略：https://www.quantopian.com/posts/evolutionary-strategy
    """
    def __init__(self):
        pass

    def prepare_data(self):
        data = OrderedDict()
        data['SPY'] = pd.read_csv('/Users/tony/zipline_data_can_delete/AAPL.csv', index_col=0,
                                  parse_dates=[['Date', 'Timestamp']])
        data['SPY'] = data['SPY'][['OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice', 'TotalVolume']]
        data['SPY'] = data['SPY'].drop(columns=['HighPrice', 'LowPrice', 'ClosePrice', 'TotalVolume'])
        # data['SPY'] = data['SPY'].loc(axis=0)[:, "OpenPrice"]  # TODO 只选取price这1列
        panel = pd.Panel(data)
        panel.major_axis = panel.major_axis.tz_localize(pytz.utc)
        # panel.minor_axis = ['open', 'high', 'low', 'close', 'volume']
        panel.minor_axis = ['open']
        return panel

    def initialize(self, context):
        context.security = symbol("SPY")
        context.window_length = 10  # Amount of prior bars to study
        context.classifier = RandomForestClassifier()  # Use a random forest classifier

        # deques are lists with a maximum length where old entries are shifted out
        context.recent_prices = deque(maxlen=context.window_length + 2)  # Stores recent prices
        context.X = deque(maxlen=500)  # Independent, or input variables
        context.Y = deque(maxlen=500)  # Dependent, or output variable

        context.prediction = 0  # Stores most recent prediction

    def handle_data(self, context, data):
        context.recent_prices.append(data[context.security].price)  # Update the recent prices
        if len(context.recent_prices) == context.window_length + 2:  # If there's enough recent price data
            # Make a list of 1's and 0's, 1 when the price increased from the prior bar
            changes = np.diff(context.recent_prices) > 0
            context.X.append(changes[:-1])  # Add independent variables, the prior changes
            context.Y.append(changes[-1])  # Add dependent variable, the final change
            if len(context.Y) >= 100:  # There needs to be enough data points to make a good model
                context.classifier.fit(context.X, context.Y)  # Generate the model
                context.prediction = context.classifier.predict(changes[1:])  # Predict
                # If prediction = 1, buy all shares affordable, if 0 sell all shares
                order_target_percent(context.security, context.prediction)
                record(prediction=int(context.prediction))

    def run_algorithm(self):
        start_time = datetime(2018, 1, 2, 9, 31, 0, 0, pytz.utc)
        end_time = datetime(2018, 2, 4, 16, 0, 0, 0, pytz.utc)
        zipline.run_algorithm(start=start_time,
                                     end=end_time,
                                     initialize=self.initialize,
                                     capital_base=100000,
                                     handle_data=self.handle_data,
                                     before_trading_start=self.before_trading_start,
                                     data_frequency='minute',
                                     data=self.prepare_data(),
                                     trading_calendar=ChineseStockCalendar(),
                                     analyze=self.analyze)


if __name__ == '__main__':
    SimpleMachineLearningStrategy().run_algorithm()

