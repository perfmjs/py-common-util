# -*- coding: utf-8 -*-
from py_common_util.zipline.chinese_stock_calendar import ChineseStockCalendar
from py_common_util.zipline.default_strategy import DefaultStrategy
from py_common_util.common.common_utils import CommonUtils
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from empyrical import cum_returns, annual_return, sharpe_ratio, max_drawdown, alpha, beta
import pandas as pd
from collections import OrderedDict
from zipline.api import order, record, symbol


class DualMovingAverageStrategy(DefaultStrategy):
    """
    参考：https://github.com/quantopian/zipline/blob/master/zipline/examples/dual_moving_average.py
    https://www.google.com/search?q=zipline+multiple+stocks&rlz=1C5CHFA_enCN643CN643&oq=zipline+multiple+stocks&aqs=chrome..69i57.809j0j9&sourceid=chrome&ie=UTF-8
    https://groups.google.com/forum/#!topic/zipline/1GFJSyRwd7w
    https://www.quantopian.com/posts/applying-strategy-to-multiple-stocks-fail
    """
    def __init__(self):
        super().__init__()

    def prepare_data(self):
        """
        AAPL.csv数据涞源：https://finance.yahoo.com/quote/AAPL/history/
        :return:
        """
        super().prepare_data()
        data = OrderedDict()
        csv_file_local = "/Users/tony/zipline_data_can_delete/AAPL.csv"
        csv_file_remote = "/tony/zipline_local_dataset/AAPL.csv"
        to_csv_file_local = "~/.zipline/data/treasury_curves.csv"
        to_csv_file_remote = "/tony/zipline_local_dataset/treasury_curves.csv"
        data['SPY'] = self.pandas.read_csv(csv_file_local, index_col=0, parse_dates=[['Date', 'Timestamp']])
        data['SPY'].to_csv(to_csv_file_local)  # 手工生成treasury_curves.csv文件
        data['SPY'] = data['SPY'][['OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice', 'TotalVolume']]
        panel = self.pandas.Panel(data)
        panel.major_axis = panel.major_axis.tz_localize(tz='utc')
        panel.minor_axis = ['open', 'high', 'low', 'close', 'volume']
        return panel

    def initialize(self, context):
        self.log.info("sid(int)=" + str(self.zipline.api.sid(0)))  # 这里的sid(0)等价symbol('SPY')
        context.sym = self.zipline.api.symbol('SPY')
        context.i = 0
        # Explicitly set the commission/slippage to the "old" value until we can
        # rebuild example data.
        # github.com/quantopian/zipline/blob/master/tests/resources/
        # rebuild_example_data#L105
        context.set_commission(self.zipline.finance.commission.PerShare(cost=.0075, min_trade_cost=1.0))
        context.set_slippage(self.zipline.finance.slippage.VolumeShareSlippage())
        # self.zipline.api.set_benchmark(self.zipline.api.symbol('SPY'))

    def before_trading_start(self, context, data):
        # 每个bar_open之前执行，对日K可选定当天待交易股票，分钟K可以用于初始化数据
        # self.log.info("before_trading_start...")
        pass

    def handle_data(self, context, data):
        # Skip first 300 days to get full windows
        context.i += 1
        if context.i < 300:
            return
        # Compute averages
        # history() has to be called with the same params
        # from above and returns a pandas dataframe.
        short_mavg = data.history(context.sym, 'price', 100, '1m').mean()
        long_mavg = data.history(context.sym, 'price', 300, '1m').mean()

        # Trading logic
        if short_mavg > long_mavg:
            # order_target orders as many shares as needed to
            # achieve the desired number of shares.
            self.zipline.api.order_target(context.sym, 100)
        elif short_mavg < long_mavg:
            self.zipline.api.order_target(context.sym, 0)

        # Save values for later inspection
        self.zipline.api.record(SPY=data.current(context.sym, "price"),
               short_mavg=short_mavg,
               long_mavg=long_mavg)

    def analyze(self, context, records):
        fig = plt.figure()
        ax1 = fig.add_subplot(211)
        records.portfolio_value.plot(ax=ax1)
        ax1.set_ylabel('Portfolio value (USD)')

        ax2 = fig.add_subplot(212)
        ax2.set_ylabel('Price (USD)')

        # If data has been record()ed, then plot it.
        # Otherwise, log the fact that no data has been recorded.
        if ('SPY' in records and 'short_mavg' in records and
                'long_mavg' in records):
            records['SPY'].plot(ax=ax2)
            records[['short_mavg', 'long_mavg']].plot(ax=ax2)

            trans = records.ix[[t != [] for t in records.transactions]]
            buys = trans.ix[[t[0]['amount'] > 0 for t in
                             trans.transactions]]
            sells = trans.ix[
                [t[0]['amount'] < 0 for t in trans.transactions]]
            ax2.plot(buys.index, records.short_mavg.ix[buys.index],
                     '^', markersize=10, color='m')
            ax2.plot(sells.index, records.short_mavg.ix[sells.index],
                     'v', markersize=10, color='k')
            plt.legend(loc=0)
        else:
            msg = 'SPY, short_mavg & long_mavg data not captured using record().'
            ax2.annotate(msg, xy=(0.1, 0.5))
            self.log.info(msg)
        plt.show()

    @CommonUtils.print_exec_time
    def run_algorithm(self):
        # data = self.ts.proapi.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        # self.log.info(data)
        start_time = self.pandas.Timestamp('2018-01-02 09:31:00', tz='utc')
        end_time = self.pandas.Timestamp('2018-02-04 16:00:00', tz='utc')
        data_frequency = 'minute'
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


def draw_return_rate_line(result):
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
    # zipline风险指标计算 (empyrical模块)  https://www.cnblogs.com/fangbei/p/8432891.html
    # https://github.com/zhanghan1990/zipline-chinese/blob/master/zipline/examples/stock_select.py
    perf = DualMovingAverageStrategy().run_algorithm()
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




