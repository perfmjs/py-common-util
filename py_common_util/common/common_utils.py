# -*- coding:utf-8 -*-
import csv


class CommonUtils:

    @staticmethod
    def write_csv(file_name, mode='w', write_fn=None):
        """
        write record to csv file
        :param file:
        :param mode: 'r','w'
        :param csvwrite_fn:
        :return:
        """
        with open(file_name, mode) as stream:
            csvwriter = csv.writer(stream)
            write_fn(csvwriter)

    @staticmethod
    def write_h5(file_name, mode='w', db_name='', shape=(1,), dtype='f', data=None):
        import h5py
        h5_file = h5py.File(file_name, mode)
        h5_dataset = h5_file.create_dataset(db_name, shape, data)
        return h5_file

    @staticmethod
    def cycle(iterable=[None]):
        """
        e.g.
        from py_common_util.common.common_utils import CommonUtils
        ...
        iter = CommonUtils.cycle([0,2,3,1])
        next(iter)->0,next(iter)->2,...,next(iter)->0,next(iter)->2,...
        :param iterable: e.g. [0,2,3,1]
        :return:
        """
        from itertools import cycle
        return cycle(iterable)

    @staticmethod
    def datetime_to_int(datetime):
        import time
        return int(time.mktime(datetime.timetuple()))

    @staticmethod
    def int_to_datetime(datetime_int):
        from datetime import datetime
        return datetime.fromtimestamp(datetime_int)

    @staticmethod
    def str_to_datetime(datetime_str, format="%Y%m%d%H%M%S"):
        from datetime import datetime
        return datetime.strptime(datetime_str, format)

    @staticmethod
    def datetime_to_str(date_time, format="%Y%m%d%H%M%S"):
        from datetime import datetime
        return datetime.strftime(date_time, format)  # 将日期转成字面整型字符串, e.g. date: 2009-12-08 16:34:00 -> '20091208163400'

    @staticmethod
    def datetime_now():
        from datetime import datetime
        return datetime.now()

    @staticmethod
    def camelcase_to_snakecase(class_name):
        """
        Convert camel-case string to snake-case.
        e.g. SuperDatasetBuilder.camelcase_to_snakecase(RecommendDatasetBuilder().__class__.__name__)
        -> "recommend_dataset_builder"
        or SuperDatasetBuilder.camelcase_to_snakecase("RecommendDatasetBuilder")
        -> "recommend_dataset_builder"
        """
        # @see tensorflow_datasets.core.naming#camelcase_to_snakecase
        import re
        _first_cap_re = re.compile("(.)([A-Z][a-z0-9]+)")
        _all_cap_re = re.compile("([a-z0-9])([A-Z])")
        s1 = _first_cap_re.sub(r"\1_\2", class_name)
        return _all_cap_re.sub(r"\1_\2", s1).lower()

    def print_exec_time(func):
        """
        装饰器：print execution time
        usage:
        @print_exec_time
        def add(x, y=10):
            return x + y
        if __name__ == '__main__':
        add(1, 2) -> "func: add(), time taken: 0.000002 seconds"
        :param func:
        :return:
        """
        def decorator_func(*args, **kwargs):
            from time import time
            before_time = time()
            rv = func(*args, **kwargs)
            print('print_exec_time->func: '+func.__name__+'()' + ', time taken: {:.3f} seconds'.format(time() - before_time))
            return rv
        return decorator_func

