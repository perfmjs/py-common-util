# -*- coding: utf-8 -*-
# 1. Warm up for 70 days
# 2. Generate 5 random momentum strategies
# 3. Run these strategies for 30 days
# 4. Pick the best of the strategies that have been run, and generate 5 new strategies derived from the top performers
# 5. Continue with this process, and make trades based off the strategy that performed the best in the past
# The random strategies have 4 "genes" in their "genome"
# derivatives determines, generally speaking, if we want to take action when the price has just a positive/negative first derivative or both a positive/negative first and second derivative
# vwap1 is the main vwap
# vwap2 is used if we have derivatives = 2
# shortlong determines whether we go short or long on upswings/downswings
# For each strategy "in testing", search through stocks that fit the criteria and take action
# Using the strategy that performed the best, make trades
import random
from collections import deque
import zipline
from zipline.finance import commission, slippage
from zipline.api import order_target, record, order_target_percent

import pandas as pd
from collections import OrderedDict
import pytz
from datetime import datetime
from contrib_lib.quant.utils.chinese_stock_calendar import ChineseStockCalendar
from contrib_lib.quant.zipline.default_strategy import DefaultStrategy


class EvolutionaryStrategy(DefaultStrategy):
    """
    进化算法策略
    参考：https://www.quantopian.com/posts/evolutionary-strategy
    """
    def __init__(self):
        super().__init__()

    def prepare_data(self):
        data = OrderedDict()
        data['SPY'] = pd.read_csv('/Users/tony/zipline_data_can_delete/AAPL.csv', index_col=0,
                                  parse_dates=[['Date', 'Timestamp']])
        data['SPY'] = data['SPY'][['OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice', 'TotalVolume']]
        panel = pd.Panel(data)
        panel.major_axis = panel.major_axis.tz_localize(pytz.utc)
        panel.minor_axis = ['open', 'high', 'low', 'close', 'volume']
        return panel

    # Initialize the needed starting variables
    def initialize(self, context):
        context.set_slippage(slippage.FixedSlippage(spread=0))
        context.set_commission(commission.PerTrade(cost=0))
        context.target_duration = 30  # How long to test strategies for
        context.num_parents = 4  # Number of parents each new species has
        context.generation_size = 5  # How many species to generate per generation
        context.frames = deque(maxlen=70)  # Store past frames for past prices
        context.species = []  # All species are stored here
        self.new_generation(context)  # Create a new generation (starts testing on 70th day)

    # Creates a new generation of size context.generation_size based off of top performers from past generations
    def new_generation(self, context):
        possible_parents = []
        for spec in context.species:
            if spec['run_duration'] >= context.target_duration: possible_parents.append(spec)
        parents = sorted(possible_parents, key=lambda k: k['value'])[-context.num_parents:]

        for i in range(context.generation_size):
            # Create new species with 4 genes from parents and a new random gene
            random_gene = random.randrange(4)
            if random_gene == 0 or len(parents) < context.num_parents:
                derivatives = random.randint(1, 2)
            else:
                derivatives = parents[random.randrange(context.num_parents)]['derivatives']

            if random_gene == 1 or len(parents) < context.num_parents:
                vwap1 = random.randint(3, 70)
            else:
                vwap1 = parents[random.randrange(context.num_parents)]['vwap1']

            if random_gene == 2 or len(parents) < context.num_parents:
                vwap2 = random.randint(2, vwap1 - 1)
            else:
                vwap2_poss = []
                for spec in parents:
                    if spec['vwap2'] < vwap1: vwap2_poss.append(spec['vwap2'])
                if len(vwap2_poss) > 0:
                    vwap2 = random.choice(vwap2_poss)
                else:
                    vwap2 = random.randint(2, vwap1 - 1)

            if random_gene == 3 or len(parents) < context.num_parents:
                shortlong = random.randrange(2)
            else:
                shortlong = parents[random.randrange(context.num_parents)]['shortlong']

            # For each species, store its genes, how long it's been run for, its value (starts at 100, similar to $100), and its positions
            context.species.append(
                {'derivatives': derivatives, 'vwap1': vwap1, 'vwap2': vwap2, 'shortlong': shortlong, 'run_duration': 0,
                 'value': 100, 'current_longs': [], 'current_shorts': []})
        return None

    # Run a specific strategy species, used on strategies with run_duration less than context.target_duration and also the best overall returner
    def run_strategy(self, key, context, data):
        strat = context.species[key]
        for sid in data:
            if strat['derivatives'] == 1:
                # If price is more or less than vwap, take action
                if data[sid].price > self.dynamicvwap(context, sid, strat['vwap1']):
                    if strat['shortlong'] == 0 and sid not in strat['current_longs']:
                        strat['current_longs'].append(sid)
                        if sid in strat['current_shorts']:
                            strat['current_shorts'].remove(sid)
                    elif strat['shortlong'] == 1 and sid not in strat['current_shorts']:
                        strat['current_shorts'].append(sid)
                        if sid in strat['current_longs']:
                            strat['current_longs'].remove(sid)
                elif data[sid].price < self.dynamicvwap(context, sid, strat['vwap1']):
                    if strat['shortlong'] == 1 and sid not in strat['current_longs']:
                        strat['current_longs'].append(sid)
                        if sid in strat['current_shorts']:
                            strat['current_shorts'].remove(sid)
                    elif strat['shortlong'] == 0 and sid not in strat['current_shorts']:
                        strat['current_shorts'].append(sid)
                        if sid in strat['current_longs']:
                            strat['current_longs'].remove(sid)

            else:
                # If two derivatives in agreement, take action
                if data[sid].price > self.dynamicvwap(context, sid, strat['vwap2']) and self.dynamicvwap(context, sid, strat[
                    'vwap2']) > self.dynamicvwap(context, sid, strat['vwap1']):
                    if strat['shortlong'] == 0 and sid not in strat['current_longs']:
                        strat['current_longs'].append(sid)
                        if sid in strat['current_shorts']:
                            strat['current_shorts'].remove(sid)
                    elif strat['shortlong'] == 1 and sid not in strat['current_shorts']:
                        strat['current_shorts'].append(sid)
                        if sid in strat['current_longs']:
                            strat['current_longs'].remove(sid)
                elif data[sid].price < self.dynamicvwap(context, sid, strat['vwap2']) and self.dynamicvwap(context, sid, strat[
                    'vwap2']) < self.dynamicvwap(context, sid, strat['vwap1']):
                    if strat['shortlong'] == 1 and sid not in strat['current_longs']:
                        strat['current_longs'].append(sid)
                        if sid in strat['current_shorts']:
                            strat['current_shorts'].remove(sid)
                    elif strat['shortlong'] == 0 and sid not in strat['current_shorts']:
                        strat['current_shorts'].append(sid)
                        if sid in strat['current_longs']:
                            strat['current_longs'].remove(sid)
        return None

    # Updates returns after a strategy is run
    def update_returns(self, key, context, data):
        strat = context.species[key]
        daily_total_returns = 0
        for sid in data:
            if sid in strat['current_longs']:
                daily_total_returns += data[sid].returns()
            elif sid in strat['current_shorts']:
                daily_total_returns -= data[sid].returns()
        if len(strat['current_longs']) + len(strat['current_shorts']) > 0:
            strat['value'] *= (daily_total_returns / (len(strat['current_longs']) + len(strat['current_shorts'])) + 1)
        return None

    # We need a special volume-weighted average price function since our num_bars isn't static
    def dynamicvwap(self, context, sid, num_bars):
        addedprices = 0
        count = 0
        for i in range(1, num_bars + 1):
            bar = context.frames[-i]
            addedprices += bar[sid].price
            count += 1
        return addedprices / count

    # This is called once per bar
    def handle_data(self, context, data):
        context.frames.append(data)  # Update the recent bars
        top_returner = {}

        # If we have enough past data:
        if len(context.frames) == 70:
            new_gen = 1
            # Find the top performer
            tested_strats = []
            for strat in context.species:
                if strat['run_duration'] >= context.target_duration:
                    tested_strats.append(strat)
            top_returners = sorted(tested_strats, key=lambda k: k['value'])
            if top_returners:
                top_returner = top_returners[-1]
            # For each species, check if it needs to be run and then run it
            for i in range(len(context.species)):
                if context.species[i]['run_duration'] < context.target_duration or context.species[i] == top_returner:

                    # Update returns, but not for the top performer to prevent bias
                    if context.species[i] != top_returner:
                        self.update_returns(i, context, data)
                        context.species[i]['run_duration'] += 1
                        new_gen = 0
                    self.run_strategy(i, context, data)

            if new_gen == 1:
                self.log.info('Current top performer:')
                self.log.info('derivatives: ' + str(top_returner['derivatives']))
                self.log.info('vwap1: ' + str(top_returner['vwap1']))
                self.log.info('vwap2: ' + str(top_returner['vwap2']))
                self.log.info('shortlong: ' + str(top_returner['shortlong']))
                self.log.info('# of positions: ' + str(len(top_returner['current_shorts']) + len(top_returner['current_longs'])))
                self.log.info('Value: ' + str(top_returner['value']))
                self.log.info('-------------')
                self.new_generation(context)  # Create new generation

            longs = []
            shorts = []
            context.portfolio.portfolio_value
            # Make trades based on the top performer
            # Buy and sell shares in 2:1 leverage with amount proportional to our starting cash
            if top_returner:
                for sid in data:
                    if sid in top_returner['current_longs']:
                        longs.append(sid)
                    elif sid in top_returner['current_shorts']:
                        shorts.append(sid)

                for sid in data:
                    if sid in longs:
                        order_target_percent(sid, 1.0 / len(longs))
                    elif sid in shorts:
                        order_target_percent(sid, -1.0 / len(shorts))
                    else:
                        order_target(sid, 0)
        try:
            top_returner['value']
        except:
            top_returner['value'] = 0
        record(num_species=len(context.species), top_value=top_returner['value'])

    def run_algorithm(self):
        # start_time = datetime(2018, 1, 2, 9, 31, 0, 0, pytz.utc)
        start_time = datetime(2018, 1, 5, 9, 31, 0, 0, pytz.utc)
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
    EvolutionaryStrategy().run_algorithm()

