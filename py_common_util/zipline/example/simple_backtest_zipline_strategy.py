# -*- coding: utf-8 -*-
from py_common_util.zipline.chinese_stock_calendar import ChineseStockCalendar
from py_common_util.zipline.default_strategy import DefaultStrategy
from py_common_util.common.common_utils import CommonUtils
from empyrical import cum_returns, annual_return, sharpe_ratio, max_drawdown, alpha, beta
import pandas as pd
from collections import OrderedDict
from trading_calendars import get_calendar


class NocodeBacktestZiplineStrategy(DefaultStrategy):
    """
    无编程回测zipline策略类
    """
    def __init__(self):
        super().__init__()

    def prepare_data(self):
        """
        AAPL.csv数据涞源：https://finance.yahoo.com/quote/AAPL/history/
        :return:
        """
        super().prepare_data()
        data_dict = OrderedDict()
        data = {
                'trade_date': pd.Series([self.pandas.Timestamp('2018-07-30 00:00:00', tz='utc'),
                                         self.pandas.Timestamp('2018-07-31 00:00:00', tz='utc'),
                                         self.pandas.Timestamp('2018-08-01 00:00:00', tz='utc')]),
                'open': pd.Series([1.0, 2.0, 1.0]),
                'high': pd.Series([1.0, 2.0, 1.0]),
                'low': pd.Series([1.0, 2.0, 1.0]),
                'close': pd.Series([201, 200, 203]),
                'volume': pd.Series([1.0, 2.0, 1.0])
                }
        data_dict["SPY"] = pd.DataFrame(data)
        data_dict["SPY"].set_index("trade_date", inplace=True)
        data_dict["SPY"]["benchmark_return"] = data_dict["SPY"]["close"].pct_change()
        data_dict["SPY"]["benchmark_return"].fillna(0, inplace=True)
        data_dict['SPY'] = data_dict['SPY'][['open', 'high', 'low', 'close', 'volume',"benchmark_return"]]
        print(data_dict["SPY"].head())
        panel = self.pandas.Panel(data_dict)
        panel.major_axis = panel.major_axis.tz_convert(tz='utc')
        panel.minor_axis = ['open', 'high', 'low', 'close', 'volume', "benchmark_return"]
        return panel

    def initialize(self, context):
        self.log.info("sid(int)=" + str(self.zipline.api.sid(0)))  # 这里的sid(0)等价symbol('SPY')
        context.sym = self.zipline.api.symbol('SPY')
        self.zipline.api.set_benchmark(context.sym)
        context.i = 0
        context.set_commission(self.zipline.finance.commission.PerShare(cost=.0075, min_trade_cost=1.0))
        context.set_slippage(self.zipline.finance.slippage.VolumeShareSlippage())

    def before_trading_start(self, context, data):
        self.log.info("before_trading_start...")
        pass

    def handle_data(self, context, data):
        self.log.info("handle_data...")
        context.i += 1
        # if context.i < 300:
        #     return
        # self.zipline.api.order(asset=context.sym, amount=100, limit_price=10.23)
        asset = self.zipline.api.symbol("SPY")
        self.zipline.api.order(asset, amount=100, limit_price=201.7)
        # self.zipline.api.order_target(context.sym, 123)
        self.zipline.api.order_target_percent(context.sym, 0.5)

    def analyze(self, context, records):
        self.log.info("analyze...")
        pass

    @CommonUtils.print_exec_time
    def run_algorithm(self):
        us_calendar = get_calendar("XNYS")
        cn_calendar = ChineseStockCalendar(data_frequency="daily")
        hk_calendar = get_calendar("XHKG")
        start_time = self.pandas.Timestamp('2018-07-30 09:31:00', tz='utc')
        end_time = self.pandas.Timestamp('2018-08-01 16:00:00', tz='utc')
        perf = self.zipline.run_algorithm(start=start_time,
                                          end=end_time,
                                          initialize=self.initialize,
                                          capital_base=100000,
                                          handle_data=self.handle_data,
                                          before_trading_start=self.before_trading_start,
                                          data_frequency="daily",
                                          data=self.prepare_data(),
                                          trading_calendar=us_calendar,
                                          analyze=self.analyze)
        return perf


def draw_return_rate_line(result):
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter
    import seaborn as sns
    sns.set_style('darkgrid')
    sns.set_context('notebook')
    ax = plt.axes()
    # 设置时间显示格式
    years_fmt = DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(years_fmt)
    # 让x轴坐标旋转45度
    labels = ax.get_xticklabels()
    plt.setp(labels, rotation=35, horizontalalignment='right')
    # 画出收益率曲线
    sns.lineplot(x='period_close',
    y='algorithm_period_return',
    data=result,
    label="AAPL")
    sns.lineplot(x='period_close',
        y='benchmark_period_return',
        data=result, label="SPX")
    plt.legend(loc='upper left')
    plt.title("return rate of AAPL and SPX")
    plt.xlabel('time')
    plt.ylabel('return rate')
    plt.show()


if __name__ == '__main__':
    # BenchmarkReturnsAndVolatility().start_of_simulation()
    perf = NocodeBacktestZiplineStrategy().run_algorithm()
    print(perf)
    print("========")
    # 画出收益曲线图
    draw_return_rate_line(perf)
    return_list = perf['returns']
    # 计算年化收益率
    ann_return = annual_return(return_list)
    # 计算累计收益率
    cum_return_list = cum_returns(return_list)
    # 计算sharp ratio
    sharp = sharpe_ratio(return_list)
    # 最大回撤
    max_drawdown_ratio = max_drawdown(return_list)
    print("年化收益率 = {:.2%}, 累计收益率 = {:.2%}, 最大回撤 = {:.2%}, 夏普比率 = {:.2f} ".format
          (ann_return, cum_return_list[-1], max_drawdown_ratio, sharp))

    returns = pd.Series(
        index=pd.date_range('2017-03-10', '2017-03-19'),
        data=(-0.012143, 0.045350, 0.030957, 0.004902, 0.002341, -0.02103, 0.00148, 0.004820, -0.00023, 0.01201)
    )
    benchmark_returns = pd.Series(
        index=pd.date_range('2017-03-10', '2017-03-19'),
        data=(-0.031940, 0.025350, -0.020957, -0.000902, 0.007341, -0.01103, 0.00248, 0.008820, -0.00123, 0.01091)
    )
    alpha_return = alpha(returns=returns, factor_returns=benchmark_returns, risk_free=0.01)
    beta_return = beta(returns=returns, factor_returns=benchmark_returns, risk_free=0.01)
    print("alpha_return", alpha_return)
    print("\nbeta_return", beta_return)
    ###############
    import numpy as np
    from empyrical import alpha_beta
    returns = np.array([.01, .02, .03, -.4, -.06, -.02])
    benchmark_returns = np.array([.02, .02, .03, -.35, -.05, -.01])
    # calculate the max drawdown
    max_drawdown(returns)
    # calculate alpha and beta
    alpha, beta = alpha_beta(returns, benchmark_returns)
    print("*********")
    print(alpha, beta)




