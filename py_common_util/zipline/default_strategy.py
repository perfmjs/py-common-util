# -*- coding: utf-8 -*-
from .abstract_strategy import AbstractStrategy


class DefaultStrategy(AbstractStrategy):
    """
    abstract_strategy.py的默认实现类
    """
    def __init__(self):
        super().__init__()

    def prepare_data(self):
        return super().prepare_data()

    def initialize(self, context):
        super().initialize(context)

    def before_trading_start(self, context, data):
        super().before_trading_start(context, data)

    def handle_data(self, context, data):
        super().handle_data(context, data)

    def analyze(self, context, records):
        super().analyze(context, records)

    def run_algorithm(self):
        return super().run_algorithm()

