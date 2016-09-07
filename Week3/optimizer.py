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

# Function: initialize
# Description: 
#   Generic initialize function. Assumes time delta for close of day (1600 hrs)
#   Gets symbol data based on startdate, enddate, and symbols
#   Returns a dictionary of the symbol data, keyed using symbols or key value 

def initialize(startdate, enddate, symbols):

    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    num_symbols = len(symbols)

    time_of_day = dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(startdate, enddate, time_of_day)
    
    symbol_data_obj = da.DataAccess('Yahoo', cachestalltime=0)
    symbol_data = symbol_data_obj.get_data(timestamps, symbols, keys)
    symbol_data_dict = dict(zip(keys, symbol_data))

    for key in keys:
        symbol_data_dict[key] = symbol_data_dict[key].fillna(method='ffill')
        symbol_data_dict[key] = symbol_data_dict[key].fillna(method='bfill')
        symbol_data_dict[key] = symbol_data_dict[key].fillna(1.0)

    return symbol_data_dict

# Function: returns_calc
# Description: 
#   Returns a list of daily returns for each symbol depending on the 
#   amount allocated to each equity

def returns_calc(startdate, enddate, symbols, allocation, frequency='daily', symbol_data_dict_arg = None):

    if symbol_data_dict_arg is None:
        print 'No dict specified'
        symbol_data_dict = initialize(startdate, enddate, symbols)
    else:
        symbol_data_dict = symbol_data_dict_arg.copy()

    close_values = symbol_data_dict['close'].values
    close_values_copy = close_values.copy()

    num_trading_days = len(close_values)
    num_symbols = len(symbols)

    tsu.returnize0(close_values_copy)
    #print 'Actual daily returns', actual_daily_returns

    print 'Close values\n', close_values_copy

    normalized_close_values = close_values / close_values[0, :]
    daily_ret_values = normalized_close_values.copy()
    tsu.returnize0(daily_ret_values)

    #print daily_ret_values

    
    daily_returns_per_equity = np.zeros((num_trading_days, len(symbols)))
    fund_daily_returns = np.zeros((num_trading_days))

    cum_ret = np.ones((num_trading_days, num_symbols))
    mult_cum_ret = np.ones((num_trading_days, num_symbols))

    for symb_index in range(num_symbols):
        mult_cum_ret[0][symb_index] =  allocation[symb_index]


    for symb_index in range(num_symbols):
        for index in range(1, num_trading_days):
            cum_ret[index][symb_index] = np.sum(daily_ret_values[index][symb_index] + cum_ret[index - 1][symb_index])
            mult_cum_ret[index][symb_index] = cum_ret[index][symb_index] * allocation[symb_index]

    #print 'Cumulative returns: \n', cum_ret
    #print 'Post allocations: \n', mult_cum_ret

    fund_cumulative_returns = np.zeros((num_trading_days))

    for day in range(num_trading_days):
        fund_cumulative_returns[day] = np.sum(mult_cum_ret[day, :])
        
            
    fund_daily_returns = fund_cumulative_returns.copy()
    tsu.returnize0(fund_daily_returns)

    print fund_daily_returns

    normalized_fund_cumulative_returns = fund_cumulative_returns / fund_cumulative_returns[0]
    total_fund_cum_ret = np.sum(normalized_fund_cumulative_returns)

    return (total_fund_cum_ret, fund_daily_returns)


# Function: mean_returns_calc
# Description: 
#   Return the mean of the returns, given the returns array per equity

def mean_returns_calc(equity_returns):
    return np.average(equity_returns)

# Function: stddev_returns_calc
# Description:
#   Return the standard deviation of the returns given the returns array of the equity
def stddev_returns_calc(equity_returns):
    return np.std(equity_returns)

# Function: cumulative_returns_calc
# Description: 
#   Returns the cumulative returns of the entire fund
#def cumulative_returns_calc


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



# Function: simulate
# Description: 
#   Takes in startdate, enddate, symbols, allocations
#   Returns mean daily returns, stddev of daily returns (volatility), sharpe ratio, total fund cumulative returns


def simulate(startdate, enddate, symbols, allocations):
    
    symbol_data_dict = initialize(startdate, enddate, symbols)

    total_fund_cumulative_returns, fund_daily_returns = returns_calc(startdate, enddate, symbols, allocations, "daily", symbol_data_dict)

    mean_returns = mean_returns_calc(fund_daily_returns)
    stddev_returns = stddev_returns_calc(fund_daily_returns)
    sharpe_ratio = sharpe_ratio_calc(mean_returns, stddev_returns)

    print 'Mean: ', mean_returns
    print 'Volatility: ', stddev_returns
    print 'Sharpe Ratio:', sharpe_ratio
    print 'Total Cumulative Returns: ', total_fund_cumulative_returns

    return (mean_returns, stddev_returns, sharpe_ratio, total_fund_cumulative_returns)

    #print daily_ret_values
    
'''
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
'''

    

    #print 'Sharpe Ratio: ', sharpe_ratio
    #print 'Std dev: ', stddev_returns
    #print 'Average: ', mean_returns
    #print 'Total cumulative return: ', total_fund_cum_ret
    
    


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

    if sys.argv[1].lower() == 'example':
        startdate = dt.datetime(2011, 1, 1)
        enddate = dt.datetime(2011, 12, 31)
        symbols = ['AAPL', 'GLD', 'GOOG', 'XOM'  ]
        allocations = [0.4, 0.4, 0.0, 0.2]
        simulate(startdate, enddate, symbols, allocations)

    elif sys.argv[1].lower() == 'lesson':
        startdate = dt.datetime(2011, 1, 1)
        enddate = dt.datetime(2011, 1, 15)
        symbols = ['AAPL', 'GLD']#'GOOG', 'XOM'  ]
        allocations = [0.6, 0.4]# 0.0, 0.2]
        simulate(startdate, enddate, symbols, allocations)

    
    


if __name__ == "__main__":
    main()


