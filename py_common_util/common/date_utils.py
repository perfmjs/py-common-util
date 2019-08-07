# -*- coding:utf-8 -*-
import time
from datetime import datetime
import datetime as dt


class DateUtils:

    @staticmethod
    def to_int(datetime):
        # 转换成时间秒, 用time.time()可以返回有小数点如0.1的秒整数
        return int(time.mktime(datetime.timetuple()))

    @staticmethod
    def int_to_datetime(datetime_int):
        return datetime.fromtimestamp(datetime_int)

    @staticmethod
    def str_to_datetime(datetime_str, format="%Y%m%d%H%M%S"):
        return datetime.strptime(datetime_str, format)

    @staticmethod
    def to_str(date_time, format="%Y%m%d%H%M%S"):
        """
        e.g. DateUtils.to_str(DateUtils.now(), format="%Y-%m-%d %H:%M:%S.%f")[:-3] = "2019-01-22 00:49:25.216"
        :param date_time: date_time类型， 如果是字符串类型则直接返回
        :param format: "%Y%m%d%H%M%S.%f" 格式为 "年月日时分秒.6位毫秒" 经[:-3]可以变为3位毫秒
        :return:
        """
        return date_time.strftime(format)  # 转成字面整型字符串, e.g. date: 2009-12-08 16:34:00 -> '20091208163400'

    @staticmethod
    def now():
        return datetime.now()

    @staticmethod
    def now_to_int():
        return DateUtils.to_int(DateUtils.now())

    @staticmethod
    def now_to_str():
        """当前时间转成string格式输出，如：2019-07-24 09:19:09.668136"""
        return DateUtils.to_str(DateUtils.now(), format="%Y-%m-%d %H:%M:%S.%f")

    @staticmethod
    def calc_duration_seconds(start_time_int, end_time_int):
        """
        :param start_time_int:
        :param end_time_int:
        :return:
        usage:
            start_time_int = DateUtils.to_int(DateUtils.now())
            DateUtils.sleep(5)
            duration = DateUtils.calc_duration_seconds(start_time_int, DateUtils.to_int(DateUtils.now()))
            print(duration)
        """
        return end_time_int - start_time_int

    @staticmethod
    def calc_delta_days(start_date=None, end_date=None, include_start_end_date=False):
        """
        计算从start_date到end_date的所有日期数组（包含start_date, end_date）
        """
        timedelta = end_date - start_date
        if include_start_end_date:
            return [start_date + dt.timedelta(days=int(i)) for i in range(0, timedelta.days+1)]
        else:
            return [start_date + dt.timedelta(days=int(i)) for i in range(1, timedelta.days)]

    @staticmethod
    def sleep(seconds):
        time.sleep(seconds)


if __name__ == '__main__':
    print(DateUtils.to_str(DateUtils.now(), format="%Y-%m-%d %H:%M:%S.%f")[:-3])
    start_date = DateUtils.str_to_datetime("20180302", "%Y%m%d")
    print(DateUtils.calc_delta_days(start_date, DateUtils.now()))
    duration = DateUtils.calc_duration_seconds(DateUtils.now_to_int(), DateUtils.to_int(DateUtils.str_to_datetime('20190109234900')))
    print(duration)
