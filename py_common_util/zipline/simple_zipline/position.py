# -*- coding: utf-8 -*-
from py_common_util.common.enhanced_ordered_dict import EnhancedOrderedDict


class Position(object):
    """
    记录每只股票的持仓情况。
    init_cash_per_stock 该股票被分配的初始回测金额，e.g. 200000
    amount 剩余持有股票份数, 不可以为负数
    income 该只股票收入 e.g. (is_buy:-|is_sell:+)(amount*price) - amount*(min_move + price*commision)
    last_price 最后一次交易的价格，用于反原计算每天浮动盈亏
    market_position 当前持仓状态，多仓1，空仓-1，无仓位0
    浮动盈亏总价值=balance_cash + 浮动amount*last_price
    """
    def __init__(self, security_code, init_cash_per_stock, amount=0, start_price=0, market_position=1):
        self.security_code = security_code
        self.init_cash_per_stock = init_cash_per_stock  # 该股票分配的初始回测金额（如：20万=100万/5只股票平分）
        self.amount = amount  # 这个amount属性没有方向, 只有正数
        self.start_amount = self.amount  # 调仓周期中的起始仓位
        self.income = 0  # init_cash_per_stock + income = 剩下的现金
        self.last_price = start_price
        self.start_price = start_price  # 调仓周期中的起始价格
        self.balance_cash = self.init_cash_per_stock  # 分配给该只股票每次交易后还剩下的静态现金（不随着股价变动而浮动，已经减去了交易时的price*amount和cost）
        self.market_position = market_position
        self.order_dict = EnhancedOrderedDict()  # 记录该股票的买卖明细（不记录刷总市值的order）：Order.uuid->Order, Order:uuid, amount, price, buy_or_sell, market_position, create_date_time

    def update(self, added_amount, new_last_price, min_move, commision, market_position=1):
        """
        added_amount可以为负数, 在多仓的情况下负数表示减仓，多仓的情况下正数表示加仓,
        若added_amount=0，表示在无交易的情况下情况下，以最新的价格还原重新计算浮动盈亏的总成本价cost
        视情况而定，回测阶段系统强行自动平仓可以不计算平仓的交易成本，即传入的min_move=0,commision=0
        """
        if self.market_position > 0:
            if added_amount > 0:
                # self.income += -abs(added_amount)*new_last_price - abs(added_amount)*(min_move + new_last_price*commision)
                # self.balance_cash = self.init_cash_per_stock + self.income
                self.balance_cash += -abs(added_amount)*new_last_price - abs(added_amount)*(min_move + new_last_price*commision)
            elif added_amount == 0:  # 相当于先卖掉旧的再买回来
                # 刷新总价值时balance_cash 和 income都不变化
                # self.income += self.amount * self.last_price - self.amount * (min_move + self.last_price * commision)
                # self.income += -self.amount * new_last_price - self.amount * (min_move + new_last_price * commision)
                pass
            elif added_amount < 0:
                # self.income += abs(added_amount) * new_last_price - abs(added_amount) * (min_move + new_last_price * commision)
                # self.balance_cash = self.init_cash_per_stock + self.income
                self.balance_cash += abs(added_amount) * new_last_price - abs(added_amount) * (min_move + new_last_price * commision)
        self.amount += added_amount
        self.last_price = new_last_price
        # 第1次交易时更新start_amount和start_price
        if self.start_amount == 0:
            self.start_amount = self.amount
        if self.start_price == 0:
            self.start_price = self.last_price

    def reinit(self, init_cash_per_stock, balance_cash=0, amount=0, start_price=0, market_position=1):
        """
        重新初始化持仓(在调仓日准备重新交易旧的持仓股票的时候使用)
        clean balance，income，last_price, 只保留amount的历史值
        :return:
        """
        self.__init__(self.security_code,
                      init_cash_per_stock=init_cash_per_stock,
                      amount=amount,
                      start_price=start_price,
                      market_position=market_position)
        self.balance_cash = balance_cash

    def to_dict(self):
        """
        Creates a dictionary representing the state of this position.
        Returns a dict object of the form:
        """
        return {
            "security_code": self.security_code,
            # "start_amount": self.start_amount,
            "amount": self.amount,
            "income": self.income,
            "balance_cash": self.balance_cash,
            "start_price": self.start_price,
            "last_price": self.last_price
            # "market_position": self.market_position
        }