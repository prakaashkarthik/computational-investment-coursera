# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

# Command Line inputs
import sys

# NumPy import
import numpy as np

# Functions that I need to implement: 
#   initialize() -- that will clear all the NaN entries and other quirks of these tools found in other tutorials
#   returns_calc(startdate, enddate, symbols, allocation, frequency='daily')
#   mean_returns_calc(startdate, enddate, symbols, allocations, frequency='daily')
#   stddev_returns_calc(startdate, enddate, symbols, allocation, frequency='daily')
#   sharpe_ratio_calc(same as above)
#   cumulative_returns_calc(same as above)


# Function: sharpe_ratio_calc
# Description: 
#   Takes in mean returns, stddev of returns, and the frequency - daily or weekly
#   Returns the sharpe ratio based on the given inputs

def sharpe_ratio_calc(mean_returns, stddev_returns,  frequency='daily'):
    num_trading_days = 252
    num_trading_weeks = 52

    if frequency is 'daily':
        multiplier = np.sqrt(num_trading_days)
    elif frequency is 'weekly':
        multiplier = np.sqrt(num_trading_weeks)
    
    sharpe_ratio = multiplier * (mean_returns/stddev_returns)

    return sharpe_ratio

# From my work laptop

# Function: simulate
# Description: 
#   Takes in startdate, enddate, symbols, allocations
#   Returns mean daily returns, stddev of daily returns (volatility), sharpe ratio, total fund cumulative returns


def simulate(startdate, enddate, symbols, allocations):
    #print startdate, ' ', enddate,' ',  symbols, ' ', allocations
    
    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    num_symbols = len(symbols)

    time_of_day = dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(startdate, enddate, time_of_day)
    
    symbol_data_obj = da.DataAccess('Yahoo', cachestalltime=0)
    symbol_data = symbol_data_obj.get_data(timestamps, symbols, keys)
    symbol_data_dict = dict(zip(keys, symbol_data))

    close_values = symbol_data_dict['close'].values
    #print 'Close values\n', close_values
    normalized_close_values = close_values / close_values[0, :]
    daily_ret_values = normalized_close_values.copy()
    tsu.returnize0(daily_ret_values)

    #print daily_ret_values
    num_trading_days = len(daily_ret_values)

    cum_ret = np.ones((num_trading_days, num_symbols))
    mult_cum_ret = np.ones((num_trading_days, num_symbols))

    for symb_index in range(num_symbols):
        mult_cum_ret[0][symb_index] =  allocations[symb_index]


    for symb_index in range(num_symbols):
        for index in range(1, num_trading_days):
            cum_ret[index][symb_index] = np.sum(daily_ret_values[index][symb_index] + cum_ret[index - 1][symb_index])
            mult_cum_ret[index][symb_index] = cum_ret[index][symb_index] * allocations[symb_index]

    #print 'Cumulative returns: \n', cum_ret
    #print 'Post allocations: \n', mult_cum_ret

    total_fund_cum_ret = 0
    for symb_index in range(num_symbols):
        total_fund_cum_ret = total_fund_cum_ret + mult_cum_ret[num_trading_days - 1][symb_index]


    #print 'Total cumulative return: ', total_fund_cum_ret
    
    total_fund_daily_cum_ret = np.zeros((num_trading_days))
    for index in range(num_trading_days):
        total_fund_daily_cum_ret[index] = np.sum(mult_cum_ret[index, :])


    #print 'Total fund daily cumulative return: \n', total_fund_daily_cum_ret
    total_fund_daily_ret = total_fund_daily_cum_ret.copy()
    tsu.returnize0(total_fund_daily_ret)

    #print 'Total fund daily returns: \n', total_fund_daily_ret

    mean_returns = np.average(total_fund_daily_ret)
    stddev_returns = np.std(total_fund_daily_ret)
    sharpe_ratio = sharpe_ratio_calc(mean_returns, stddev_returns)

    #print 'Sharpe Ratio: ', sharpe_ratio
    #print 'Std dev: ', stddev_returns
    #print 'Average: ', mean_returns
    #print 'Total cumulative return: ', total_fund_cum_ret
    
    return (mean_returns, stddev_returns, sharpe_ratio, total_fund_cum_ret)


# Function: get_digits
# Description: 
#   Takes in a number
#   Returns an array containing each digit
#   Example: 9075 = [9, 0, 7, 5]

def get_digits(number):
    
    number_copy = number
    number_arr = []

    while number_copy > 0:
        number_arr.append(number_copy % 10)
        number_copy = number_copy/10

    return number_arr




# Function: Optimizer
# Description: 
#   Takes the startdate, enddate, symbols 
#   Runs simulate for all legal allocations in 10% increments
#   Keeps track of the best sharpe ratio and corresponding allocation
#   TODO: What if the increment is less than 10%? 

def optimizer(startdate, enddate, symbols):

    best_sharpe_ratio = 0
    best_opt = []
    delta = 0.1
    delta_array = [0.0 + i*delta for i in range(0, 11)]

    allocation = np.zeros((len(symbols)))
    possible_allocations = []

    num_symbols = len(symbols)
    lower = np.power(10, num_symbols - 1 )
    higher = np.power(10, len(symbols) ) - 1


    for i in range(lower, higher):
        arr = get_digits(i)
        div_arr = arr
        if np.sum(arr) == 10:
            div_arr[:] = [x / 10.0 for x in arr]
            possible_allocations.append(div_arr)

    for index in range(len(symbols)):
        ones_alloc = np.zeros((len(symbols)))
        ones_alloc[index] = 1.0
        possible_allocations.append(ones_alloc)


    for alloc in range(len(possible_allocations)):
        mean, stddev, sharpe, cum_ret = simulate(startdate, enddate, symbols, possible_allocations[alloc])
        if sharpe > best_sharpe_ratio:
            best_sharpe_ratio = sharpe
            best_opt = possible_allocations[alloc]


    print 'Best Sharpe Ratio: ', best_sharpe_ratio
    print 'Best allocation: ', best_opt
    
    

def main():

    #Q1 

    startdate = dt.datetime(2011, 1, 1)
    enddate = dt.datetime(2011, 12, 31)
    symbols = ['AAPL', 'GLD', 'GOOG', 'XOM'  ]
    allocations = [0.4, 0.4, 0.0, 0.2]

    simulate(startdate, enddate, symbols, allocations)
    


if __name__ == "__main__":
    main()


