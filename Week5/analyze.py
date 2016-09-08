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

# CSV parser
import csv

# Defaultdict to initialize empty dictionary
from collections import defaultdict


def get_fund_properties(cumulative_returns):

    total_fund_daily_return = []
    for d in range(len(cumulative_returns)):
        total_fund_daily_return.append(float(cumulative_returns[d] / cumulative_returns[0]))

    total_fund_daily_return = tsu.returnize0(total_fund_daily_return)

    fund_average = np.average(total_fund_daily_return)
    fund_stddev = np.std(total_fund_daily_return)
    fund_sharpe_ratio = np.sqrt(252) * (fund_average / fund_stddev) 

    return (fund_average, fund_stddev, fund_sharpe_ratio)



def main():

    values_file = sys.argv[1]
    benchmark_symbol = sys.argv[2]

    symbols_list = []
    symbols_list.append(benchmark_symbol)

    all_dates = []
    fund_daily_total = []
    
    reader = csv.reader(open(values_file, 'rU'), delimiter=',')

    # Scan the CSV file and store are relevant informaton
    for row in reader:
        year = int(row[0])
        month = int(row[1])
        date = int(row[2])
        fund_returns = float(row[3])

        full_date = dt.datetime(year, month, date, 16)
        all_dates.append(full_date)
        fund_daily_total.append(fund_returns)

    first_date = all_dates[0]
    last_date = all_dates[len(all_dates) - 1]

   
    # Getting the benchmark symbol's close values
    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    
    time_of_day = dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(first_date, last_date, time_of_day)
    
    symbol_data_obj = da.DataAccess('Yahoo', cachestalltime=0)
    symbol_data = symbol_data_obj.get_data(timestamps, symbols_list, keys)
    symbol_data_dict = dict(zip(keys, symbol_data))

    close_values = symbol_data_dict['close'].values
  
    # Calculating the cumulative return ratio for the fund and benchmark
    total_fund_cum_return = fund_daily_total[len(fund_daily_total) - 1] / fund_daily_total[0]
    total_benchmark_cum_return = float(close_values[len(close_values) - 1] / close_values[0])

    # Getting rest of the properties for the fund and benchmark
    fund_average, fund_stddev, fund_sharpe_ratio = get_fund_properties(fund_daily_total) 
    benchmark_average, benchmark_stddev, benchmark_sharpe_ratio = get_fund_properties(close_values)

    print '\n'

    print "Total fund return: ", total_fund_cum_return
    print "Fund average daily return: ", fund_average
    print "Fund standard deviation of returns: ", fund_stddev
    print "Fund Sharpe Ratio: ", fund_sharpe_ratio

    print '\n\n'

    print "Total benchmark return: ", total_benchmark_cum_return
    print "benchmark average daily return: ", benchmark_average
    print "benchmark standard deviation of returns: ", benchmark_stddev
    print "benchmark Sharpe Ratio: ", benchmark_sharpe_ratio

    print '\n'


if __name__ == "__main__":
	main()


