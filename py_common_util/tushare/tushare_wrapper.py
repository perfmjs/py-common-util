# -*- coding:utf-8 -*-
import tushare as ts

from py_common_util.tushare import PandasUtils
from py_common_util.tushare import MySQLUtils
import datetime
import time
'''
ref: http://tushare.org/
ref: 一个提升选股技能和效果的接口 https://mp.weixin.qq.com/s/tzaV8sfhF6BNJP83cI_q2g
'''


class TushareWrapper(object):

    @property
    def db_name(self):
        return 'tushare_2017'

    @property
    def last_trading_date(self):
        """每个交易日收盘后更新trading_date, tushare在交易日17:00后更新最新数据文件"""
        """如需补抓历史(N-x, N)天的历史数据，则将last_trading_date设为最新日期，调用daily_real_data_update()后再将start_date设为N-x日期调hist_k_data_update()"""
        return '20180510'

    def __init__(self):
        print("tushare -v: " + ts.__version__)
        self.mysqlUtils = MySQLUtils()
        self.pandasUtils = PandasUtils()

    def daily_real_data_update(self, trading_date=None):
        trading_date = self.last_trading_date if trading_date is None else trading_date
        print("每日实时数据更新，dailyUpdate()..., trading_date=" + trading_date)
        print('注意：store_stock_basics和store_index应在每个交易日的23:59前就更新')
        self.store_stock_basics(trading_date)
        self.store_index(trading_date)
        ##########################################
        # self.store_today_all(trading_date)  # 有问题(20171020)
        # self.store_sina_dd(trading_date=trading_date)  # 有问题(20171019)
        # self.store_top_data(trading_date)
        # self.store_stock_classified_data(trading_date)

    def hist_k_data_update(self, special_codes=[], from_date='', end_date='', trading_date=None, autype='qfq', ktype='D', index=False, should_exclude_saved_code_as_rerun=True):
        """更新历史K线数据支持断开续取, 注意应每日备份该方法产生的数据"""
        """特别注意：该表数据巨大，操作时要特别谨慎！只有在每个新交易日第1次运行该方法的时候should_exclude_saved_code_as_rerun才为False并且设置from_date=trading_date。第2次及以后应为True"""
        """from_date/end_date, e.g. '20171013' """
        """注意：df为空的情况，原因是抓取页面的HTML结构或页面JSON有问题"""
        """注意：应该在开盘前抓取上个交易日的历史数据"""
        trading_date = self.last_trading_date if trading_date is None else trading_date
        excluded_codes = []
        if should_exclude_saved_code_as_rerun:
            saved_codes = tushare_wrapper.query_all_k_data_stock_code(autype=autype, ktype=ktype, index=index)
            excluded_codes = saved_codes
            print("as re-run, saved_codes=" + str(saved_codes) + ", len(saved_codes)=" + str(len(saved_codes)))
        print("hist_k_data_update()..., from_date=%s, end_date=%s, trading_date=%s" % (from_date, end_date, trading_date))
        self.store_k_data(special_codes=special_codes, excluded_codes=excluded_codes, from_date=from_date, end_date=end_date, autype=autype, ktype=ktype, index=index, trading_date=trading_date)

    def store_top_data(self, trading_date=None):
        """龙虎榜数据: 龙虎榜数据接口提供历史龙虎榜上榜股票数据"""
        trading_date = self.last_trading_date if trading_date is None else trading_date
        # 每日龙虎榜列表
        print('top_list...')
        top_df = ts.top_list(self.stock_date_format(trading_date))
        self.mysqlUtils.append_data(top_df, 'top_list')
        # 个股上榜统计
        print('cap_tops...')
        cap_tops_df = ts.cap_tops()
        cap_tops_df['date'] = trading_date
        self.mysqlUtils.append_data(cap_tops_df, 'cap_tops')
        # 营业部上榜统计
        print('broker_tops...')
        broker_tops_df = ts.broker_tops()
        broker_tops_df['date'] = trading_date
        self.mysqlUtils.append_data(broker_tops_df, 'broker_tops')
        # 龙虎榜机构席位追踪
        print('inst_tops...')
        inst_tops_df = ts.inst_tops()
        inst_tops_df['date'] = trading_date
        self.mysqlUtils.append_data(inst_tops_df, 'inst_tops')
        # 龙虎榜机构席位成交明细
        print('inst_detail...')
        inst_detail_df = ts.inst_detail()
        self.mysqlUtils.append_data(inst_detail_df, 'inst_detail')

    def store_stock_classified_data(self, trading_date=None):
        """股票分类数据, 需要逐个抓取入库"""
        trading_date = self.last_trading_date if trading_date is None else trading_date
        # 行业分类
        # print('get_industry_classified...')
        # industry_df = ts.get_industry_classified()  # 修改了该方法里的代码
        # industry_df['date'] = trading_date
        # self.mysqlUtils.append_data(industry_df, 'industry_classified')
        # 概念分类
        # print('get_concept_classified...')
        # concept_df = ts.get_concept_classified()  # 修改了该方法里的代码
        # concept_df['date'] = trading_date
        # self.mysqlUtils.append_data(concept_df, 'concept_classified')
        # ####以下数据可以一次性获取
        # 地域分类
        # print('get_area_classified...')
        # area_df = ts.get_area_classified()
        # area_df['date'] = trading_date
        # self.mysqlUtils.append_data(area_df, 'area_classified')
        # 中小板分类, 获取中小板股票数据，即查找所有002开头的股票
        # print('get_sme_classified...')
        # sme_df = ts.get_sme_classified()
        # sme_df['date'] = trading_date
        # self.mysqlUtils.append_data(sme_df, 'sme_classified')
        # 创业板分类: 获取创业板股票数据，即查找所有300开头的股票
        # print('get_gem_classified...')
        # gem_df = ts.get_gem_classified()
        # gem_df['date'] = trading_date
        # self.mysqlUtils.append_data(gem_df, 'gem_classified')
        # 风险警示板分类: 获取风险警示板股票数据，即查找所有st股票
        # print('get_st_classified...')
        # st_df = ts.get_st_classified()
        # st_df['date'] = trading_date
        # self.mysqlUtils.append_data(st_df, 'st_classified')
        # # 沪深300成份及权重: 获取沪深300当前成份股及所占权重
        ####以下有问题 20171021
        # print('get_hs300s')
        # hs300s_df = ts.get_hs300s()
        # hs300s_df['date'] = trading_date
        # self.mysqlUtils.append_data(hs300s_df, 'hs300s')
        # # 上证50成份股
        # print('get_sz50s...')
        # sz50s_df = ts.get_sz50s()
        # sz50s_df['date'] = trading_date
        # self.mysqlUtils.append_data(sz50s_df, 'sz50s')
        # # 中证500成份股(有问题：20171018)
        # print('get_zz500s...')
        # zz500s_df = ts.get_zz500s()
        # zz500s_df['date'] = trading_date
        # self.mysqlUtils.append_data(zz500s_df, 'zz500s')
        # 终止上市股票列表: 获取已经被终止上市的股票列表，数据从上交所获取，目前只有在上海证券交易所交易被终止的股票。
        # print('get_terminated...')
        # terminated_df = ts.get_terminated()
        # terminated_df['date'] = trading_date
        # self.mysqlUtils.append_data(terminated_df, 'terminated')
        # 暂停上市股票列表: 获取被暂停上市的股票列表，数据从上交所获取，目前只有在上海证券交易所交易被终止的股票。
        # print('get_suspended...')
        # suspended_df = ts.get_suspended()
        # suspended_df['date'] = trading_date
        # self.mysqlUtils.append_data(suspended_df, 'suspended')

    def store_stock_basics(self, trading_date=None):
        print("get_stock_basics()......trading_date=%s" % trading_date)
        df = ts.get_stock_basics(self.stock_date_format(date=trading_date))
        df['date'] = trading_date
        self.mysqlUtils.append_data(df, 'stock_basics')

    def store_k_data(self, special_codes=[], excluded_codes=[], from_date='', end_date='', autype='qfq', ktype='D', index=False, trading_date=None):
        start_time = time.time()
        print("store_k_data()..., from_date=%s, end_date=%s, trading_date=%s, ktype=%s, index=%s" % (from_date, end_date, trading_date, ktype, index))
        original_table_name = 'k_data_'
        table_name = 'k_data_'
        # D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟，默认为D
        if ktype == 'D':
            original_table_name = 'k_index_day' if index else 'k_data_day'
        elif ktype == 'W':
            original_table_name = 'k_index_week' if index else 'k_data_week'
        elif ktype == 'M':
            original_table_name = 'k_index_month' if index else 'k_data_month'
        elif ktype == '5':
            original_table_name = 'k_index_5min' if index else 'k_data_5min'
        elif ktype == '15':
            original_table_name = 'k_index_15min' if index else 'k_data_15min'
        elif ktype == '30':
            original_table_name = 'k_index_30min' if index else 'k_data_30min'
        elif ktype == '60':
            original_table_name = 'k_index_60min' if index else 'k_data_60min'
        if autype == 'qfq':
            original_table_name += '_qfq'
        elif autype == 'hfq':
            original_table_name += '_hfq'
        """特别注意：为防止重复保存或弄乱已有的巨大的历史数据，每次重新保存数据时都重建新表，待检查无误时再谨慎运行增量更新的SQL"""
        """
        增量更新SQL:
        INSERT INTO k_index_day_qfq (`index`, date, open, close, high, low, volume, code)  
        SELECT `index`, date, open, close, high, low, volume, code
          FROM `k_index_day_qfq_20171017`
        """
        if len(special_codes) > 0:
            table_name = original_table_name + "_" + str(special_codes) + '_' + trading_date
        else:
            table_name = original_table_name + '_' + trading_date
        print("hist k Data will be save to table_name: " + table_name)
        print("Please copy SQL and execute manumally: \n" + "INSERT INTO %s (`index`, date, open, close, high, low, volume, code)  \n" \
        "SELECT `index`, date, open, close, high, low, volume, code \n" "FROM `%s`" % (original_table_name, table_name))

        if index:
            tupes = self.query_all_index_code(trading_date)
        else:
            tupes = self.query_all_stock_code(trading_date)
        step = 0
        for code, time_to_market in tupes:
            step += 1
            if len(special_codes) > 0 and code not in special_codes:
                continue
            category_code = code
            if index:
                index_category = ''
                if code.find('000') == 0:
                    index_category = 'sh'
                elif code.find('399') == 0:
                    index_category = 'sz'
                category_code = index_category + code
            # 新股的time_to_market为0
            if (time_to_market < 1 and not index) or (category_code in excluded_codes):
                print("code: " + str(code) + " was excluded! or time_to_market(only for new stock):" + str(time_to_market) + " < 1")
                continue
            if step < 1 or ((step + 1) % 100 == 0) or ((step + 1) >= self.get_row_num(tupes)):
                print("store_k_data... step=%d, total=%d" % (step+1, self.get_row_num(tupes)))
            df = self.get_k_data(code=code,
                                 autype=autype,
                                 ktype=ktype,
                                 index=index,
                                 start=self.stock_date_format(str(time_to_market) if (from_date == '' or from_date is None) else from_date),
                                 end='' if (end_date == '' or end_date is None) else self.stock_date_format(trading_date))
            self.mysqlUtils.append_data(df, table_name)  # 表k_data_day/k_index_day已被手工重建索引(类型：text->varchar, 索引：index,code/code)，删表结构时需要谨慎
            print("saved_codes(should be exclude as re-run):" + str(code) + ", df row num: " + str(self.get_row_num(df)))
        print("store_k_data is ok...total take time(seconds): %d" % (time.time() - start_time))

    def query_all_stock_code(self, trading_date=None):
        df = self.pandasUtils.read_sql("SELECT code, timeToMarket FROM " + self.db_name + ".stock_basics where date=" + trading_date)
        return df.values

    def query_all_index_code(self, trading_date=None):
        df = self.pandasUtils.read_sql("SELECT code, 0 FROM " + self.db_name + ".index_data where date=" + trading_date)
        return df.values

    def query_stock_time_to_market(self, code):
        """取上市时间作为历史数据的start date(e.g. 19900101), 0代表新股尚未上市的股票"""
        df = self.pandasUtils.read_sql("SELECT timeToMarket FROM " + self.db_name + ".stock_basics where code='" + code + "'")
        return df.timeToMarket.values

    def query_all_k_data_stock_code(self, autype='qfq', ktype='D', index=False):
        """获取已经保存到K线表里的所有股票code或指数code"""
        print("query_all_k_data_stock_code..., autype=%s, ktype=%s, index=%s" % (autype, ktype, index))
        table_name = ''
        if ktype == 'D':
            table_name = 'k_index_day' if index else 'k_data_day'
        elif ktype == 'W':
            table_name = 'k_index_week' if index else 'k_data_week'
        elif ktype == 'M':
            table_name = 'k_index_month' if index else 'k_data_month'
        elif ktype == '5':
            table_name = 'k_index_5min' if index else 'k_data_5min'
        elif ktype == '15':
            table_name = 'k_index_15min' if index else 'k_data_15min'
        elif ktype == '30':
            table_name = 'k_index_30min' if index else 'k_data_30min'
        elif ktype == '60':
            table_name = 'k_index_60min' if index else 'k_data_60min'
        if autype == 'qfq':
            table_name += '_qfq'
        elif autype == 'hfq':
            table_name += '_hfq'
        df = self.pandasUtils.read_sql("SELECT distinct(code) FROM " + self.db_name + "." + table_name)
        return df.values.flatten()  # e.g. [['000005'],['000006']] -> ['000005', '000006']

    def get_k_data(self, code=None, autype='qfq', start='', end='', ktype='D', index=False):
        """ 本接口只能获取近3年的日线index数据，适合搭配均线数据进行选股和分析，如果需要全部历史数据，请调用接口get_h_data() """
        # print("get_k_data()......,code=%s, start=%s, end=%s, ktype=%s, index=%s" % (code, start, end, ktype, index))
        df = ts.get_k_data(code=code, autype=autype, start=start, end=end, ktype=ktype, index=index, retry_count=10)
        return df

    def get_h_data(self, code=None, from_date=None, end_date=None, index=False, autype='qfq', drop_factor=False):
        """获取所有复权的历史数据, 取前复权的数据"""
        """start/end, e.g. '20171017'"""
        print("get_h_data()......")
        df = ts.get_h_data(code=code,
                           start=self.stock_date_format(from_date),
                           end=self.stock_date_format(end_date),
                           index=index,
                           autype=autype,
                           drop_factor=drop_factor)
        return df

    def store_today_all(self, date=None):
        """一次性获取最近一个日交易日所有股票的交易数据"""
        """ 数据每日盘中实时更新, 应该盘后抓取当天的最新数据 """
        print("store_today_all()......")
        df = ts.get_today_all()
        df['date'] = self.now_date_str() if date is None else date
        self.mysqlUtils.append_data(df, 'today_all')

    def store_index(self, trading_date=None):
        """获取大盘指数实时行情列表，以表格的形式展示大盘指数实时行情, 收盘后就是日K历史的行情"""
        print("store_index()......")
        trading_date = self.last_trading_date if trading_date is None else trading_date
        df = ts.get_index()
        df['date'] = trading_date
        self.mysqlUtils.append_data(df, 'index_data')

    def store_sina_dd(self, vol=400, trading_date=None):
        """获取大单交易数据，默认为大于等于400手，数据来源于新浪财经"""
        print("store_sina_dd()......trading_date=" + trading_date)
        date = self.stock_date_format(date=trading_date)
        step = 0
        tupes = self.query_all_stock_code(trading_date)
        for code, _ in tupes:
            df = ts.get_sina_dd(code=code, date=date, vol=vol)
            if df is not None:
                step += 1
                if step < 1 or ((step + 1) % 100 == 0) or ((step + 1) >= self.get_row_num(tupes)):
                    print("step=%d, total=%d" % (step+1, self.get_row_num(tupes)))
                df['date'] = trading_date
                self.mysqlUtils.append_data(df, 'sina_dd')

    def stock_date_format(self, date='19900101', from_format='%Y%m%d', to_format='%Y-%m-%d'):
        """e.g. 19900101->1990-01-01"""
        if date == '0' or date == '':
            return ''
        if date is None:
            return None
        return datetime.datetime.strptime(date, from_format).strftime(to_format)

    def now_date_str(self):
        return datetime.datetime.now().strftime('%Y%m%d')

    def get_row_num(self, df=None):
        if df is None:
            return 0
        return df.shape[0]


if __name__ == '__main__':
    tushare_wrapper = TushareWrapper()
    print("(18:00->24:00, 00:00->9:00)请尽量在每个交易日的盘后及第2天的开盘前抓取行情数据。。。。。。")
    # tushare_wrapper.daily_real_data_update()  # 增量每日实时数据更新
    # 增量每日更新(第1次更新should_exclude_saved_code_as_rerun=False)
    # tushare_wrapper.hist_k_data_update(index=True,
    #                                    # special_codes=['000001'],
    #                                    from_date=tushare_wrapper.last_trading_date, # ''为历史最早的交易日
    #                                    end_date=tushare_wrapper.last_trading_date,  # ''为最近交易日
    #                                    autype='qfq',
    #                                    ktype='D',
    #                                    should_exclude_saved_code_as_rerun=False)
    # tushare_wrapper.hist_k_data_update(index=False,
    #                                    from_date=tushare_wrapper.last_trading_date,  # ''为历史最早的交易日
    #                                    end_date=tushare_wrapper.last_trading_date,   # ''为最近交易日
    #                                    autype='qfq',
    #                                    ktype='D',
    #                                    should_exclude_saved_code_as_rerun=False)  # 全量从第1行开始insert


