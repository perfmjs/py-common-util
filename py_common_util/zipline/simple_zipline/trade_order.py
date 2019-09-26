# -*- coding: utf-8 -*-
from decimal import Decimal
from sys import float_info
import numpy as np
import math
from py_common_util.common.enhanced_ordered_dict import EnhancedOrderedDict
from py_common_util.zipline.simple_zipline.position import Position


class TradeOrder(object):
    """
    订单处理, 参考：zipline.TradingAlgorithm
    https://github.com/quantopian/zipline/blob/master/zipline/finance/ledger.py
    https://github.com/quantopian/zipline/blob/master/zipline/finance/order.py
    """
    @property
    def benchmark_security_code(self):
        return self._benchmark_security_code

    @property
    def bar_data(self):
        return self._bar_data

    @property
    def min_move(self):
        return self._min_move

    @property
    def commission(self):
        return self._commission

    @property
    def position_dict(self):
        return self._position_dict

    @property
    def multiple_order_position_dict(self):
        return self._multiple_trade_order_dict

    def __init__(self):
        self._benchmark_security_code = None
        self._bar_data = None
        self._commission = None
        self._min_move = 0.0  # TODO default value is 0.01， 目前让其为0
        self._position_dict = EnhancedOrderedDict()  # 每只股票代码->1个Position对象

    def do_init(self, bar_data, commission):
        self._bar_data = bar_data
        self._commission = commission

    def reinit_position_dict(self, target_security_init_cash_list):
        """
        重新初始化所有股票的持仓
        @:param target_security_init_cash_list e.g. {"00700.HK": {"init_cash_per_stock":333333, "balance_cash":0}}
        """
        for target_security_code in target_security_init_cash_list.keys():
            new_init_cash = target_security_init_cash_list[target_security_code]["init_cash_per_stock"]
            balance_cash = target_security_init_cash_list[target_security_code]["balance_cash"]
            target_position = self.position_dict.get(target_security_code)
            if target_position:
                self.position_dict.get(target_security_code).reinit(init_cash_per_stock=new_init_cash,
                                                                    balance_cash=balance_cash,
                                                                    amount=target_position.amount,
                                                                    start_price=0)
            else:
                self.position_dict[target_security_code] = Position(target_security_code, init_cash_per_stock=new_init_cash)
        # 删除非target_security_init_cash_list里的所有position
        keys = [key for key in self.position_dict.keys()]
        for security_code in keys:
            if security_code not in target_security_init_cash_list:
                self.remove_position(security_code)

    def remove_position(self, security_code):
        if security_code in self.position_dict:
            del self.position_dict[security_code]

    def order_target(self,
                     security_code,
                     target,
                     limit_price=None,
                     stop_price=None,
                     style=None):
        """
        参考：zipline.api.order_target()
        :return 返回提交委托交易的股票数量和价格 e.g. (1, 33.34)
        """
        if not self._can_order_asset(security_code):
            return 0, 0
        amount = self._calculate_order_target_amount(security_code, target)
        return self.order(security_code, amount,
                          limit_price=limit_price,
                          stop_price=stop_price,
                          style=style)

    def order(self,
              security_code,
              amount,
              limit_price=None,
              stop_price=None,
              style=None):
        """
        amount 0-不交易，仅仅按最新价刷新该股票持仓总价值；负数-sell(减仓)；正数-buy(加仓)
        参考：zipline.api.order(), zipline.TradingAlgorithm()
        :return 返回提交委托交易的股票数量和价格 e.g. (1, 33.34)
        """
        if amount == 0:
            # amount=0-不交易，仅仅按最新价刷新该股票持仓总价值
            if self.position_dict.get(security_code):
                self.position_dict.get(security_code).update(0, limit_price, 0, 0, market_position=1)
            return 0, limit_price
        if not self._can_order_asset(security_code):
            return 0, 0
        try:
            self._validate_order_params(security_code, amount, limit_price, stop_price, style)
        except Exception as e:
            print("order validation error：%s" % str(e))
            return 0, 0
        amount, handled_limit_price = self._calculate_order(security_code, amount, limit_price, stop_price, style)
        if self.position_dict.get(security_code):
            self.position_dict.get(security_code).update(amount, handled_limit_price, self.min_move, self.commission, market_position=1)
        # for security_code in self.position_dict.keys():
        #     print("order....", self.position_dict[security_code].to_dict())
        return amount, handled_limit_price

    def _validate_order_params(self,
                              security_code,
                              amount,
                              limit_price,
                              stop_price,
                              style):
        if style:
            if limit_price:
                raise Exception(msg="Passing both limit_price and style is not supported.")
            if stop_price:
                raise Exception(msg="Passing both stop_price and style is not supported.")
        # TODO 其它校验：amount>0, 买受最大可交易额限制，是否持仓有足够的股票数量可以卖，下单最小股数（目前简单的以100的整数倍计算）
        if amount == 0:
            raise Exception("amount can not be equals to 0")
        if amount > 0:
            if self.position_dict.get(security_code):
                if self.position_dict.get(security_code).balance_cash < amount * limit_price:
                    pass
                    # TODO self.position_dict.get(security_code).balance_cash 应为总持仓的total_balance_cash，先注释该validate
                    # raise Exception("security_code=%s, amount=%s, limit_price=%s, balance_cash=%s, buy order balance cash is not enough!!!" % (security_code, str(amount), str(limit_price), str(self.position_dict.get(security_code).balance_cash)))

    def _asymmetric_round_price(self, price, prefer_round_down, tick_size=0.01, diff=0.95):
        """
        Asymmetric rounding function for adjusting prices to the specified number
        of places in a way that "improves" the price. For limit prices, this means
        preferring to round down on buys and preferring to round up on sells.
        For stop prices, it means the reverse.
        If prefer_round_down == True:
            When .05 below to .95 above a specified decimal place, use it.
        If prefer_round_down == False:
            When .95 below to .05 above a specified decimal place, use it.

        In math-speak:
        If prefer_round_down: [<X-1>.0095, X.0195) -> round to X.01.
        If not prefer_round_down: (<X-1>.0005, X.0105] -> round to X.01.
        """
        precision = self._number_of_decimal_places(tick_size)
        multiplier = int(tick_size * (10 ** precision))
        diff -= 0.5  # shift the difference down
        diff *= (10 ** -precision)  # adjust diff to precision of tick size
        diff *= multiplier  # adjust diff to value of tick_size
        # Subtracting an epsilon from diff to enforce the open-ness of the upper
        # bound on buys and the lower bound on sells.  Using the actual system
        # epsilon doesn't quite get there, so use a slightly less epsilon-ey value.
        epsilon = float_info.epsilon * 10
        diff = diff - epsilon
        # relies on rounding half away from zero, unlike numpy's bankers' rounding
        rounded = tick_size * self._consistent_round(
            (price - (diff if prefer_round_down else -diff)) / tick_size
        )
        if self._tolerant_equals(rounded, 0.0):
            return 0.0
        return rounded

    def _calculate_order(self, security_code, amount, limit_price=None, stop_price=None, style=None):
        amount = self._round_order(amount)
        is_buy = amount > 0
        handled_limit_price = self._asymmetric_round_price(limit_price, is_buy)
        return amount, handled_limit_price

    def _round_order(self, amount):
        """
        Convert number of shares to an integer.
        By default, truncates to the integer share count that's either within
        .0001 of amount or closer to zero.
        E.g. 3.9999 -> 4.0; 5.5 -> 5.0; -5.5 -> -5.0
        """
        return int(self._round_if_near_integer(amount))

    def _round_if_near_integer(self, a, epsilon=1e-4):
        """
        Round a to the nearest integer if that integer is within an epsilon
        of a.
        """
        if abs(a - round(a)) <= epsilon:
            return round(a)
        else:
            return a

    def _consistent_round(self, val):
        if (val % 1) >= 0.5:
            return np.math.ceil(val)
        else:
            return round(val)

    def _number_of_decimal_places(self, n):
        """
        Compute the number of decimal places in a number.
        Examples
        --------
        >>> number_of_decimal_places(1)
        0
        >>> number_of_decimal_places(3.14)
        2
        >>> number_of_decimal_places('3.14')
        2
        """
        decimal = Decimal(str(n))
        return -decimal.as_tuple().exponent

    def _tolerant_equals(self, a, b, atol=10e-7, rtol=10e-7, equal_nan=False):
        """Check if a and b are equal with some tolerance.
        Parameters
        ----------
        a, b : float
            The floats to check for equality.
        atol : float, optional
            The absolute tolerance.
        rtol : float, optional
            The relative tolerance.
        equal_nan : bool, optional
            Should NaN compare equal?
        See Also
        --------
        numpy.isclose
        Notes
        -----
        This function is just a scalar version of numpy.isclose for performance.
        See the docstring of ``isclose`` for more information about ``atol`` and
        ``rtol``.
        """
        if equal_nan and np.isnan(a) and np.isnan(b):
            return True
        return math.fabs(a - b) <= (atol + rtol * math.fabs(b))

    def _calculate_order_target_amount(self, security_code, target):
        if self.position_dict.get(security_code):
            current_position = self.position_dict.get(security_code).amount
            target -= current_position
        return target

    def _can_order_asset(self, security_code):
        return self.bar_data.can_trade(security_code)

    def set_benchmark(self, benchmark_security_code):
        self._benchmark_security_code = benchmark_security_code

