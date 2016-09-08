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

''' 
Algorithm:
	Scan the command line arguments, get the initial sum, the orders.csv, 
	and prepare the file to be written to. Initial sum will be the first
	member of the list/array of daily returns

	Scan the orders.csv for all the different symbols we'll be trading, and
	for all the relevant dates. 

	Sort the dates, get information for that range and put it in an object. 

	Create a class "orders" which has symbol, buy/sell, num_of_shares as it's data members. 
	Create a hash map with the date being the key and list of "orders" as values. 
	As you scan orders.csv, make changes as necessary to the hashmap

	Now, if necessary, sort the hashmap according to date

	Foreach key
		Foreach order in hashmap_value
			perform_transaction()
			append new total fund value to list of daily returns

	Voila. 

'''

class Orders:

	def __init__ (self, full_date, symb, orderType, shares):
		self.symbol = symb
		self.order_type = orderType
		self.num_of_shares = shares
		self.full_date = full_date

	def print_order(self):
		print 'Symbol: ', self.symbol
		print 'Order type:', self.order_type
		print 'Number of shares:', self.num_of_shares
		print 'Date of order:', self.full_date

class Portfolio:

    def __init__(self, cash_amount, holdings_total):
        self.cash_amount = cash_amount
        self.holdings_per_symbol = {}
        self.holdings_total = 0
        self.total = self.cash_amount

    def total_calc(self):
        self.holdings_total = 0
        for symb in self.holdings_per_symbol:
            self.holdings_total += self.holdings_per_symbol[symb]
        
        self.total = self.cash_amount + self.holdings_total
        return self.total

    def print_portfolio(self):
        print 'Cash available: ', self.cash_amount
        for symb in self.holdings_per_symbol:
            print 'Cash in ', symb, ':', self.holdings_per_symbol[symb]
        print 'Portfolio Total: ', self.total


def execute_order(order, shares_per_symbol, database, portfolio):

	price = database[3][order.symbol][order.full_date]

	if order.order_type == 'Buy':
            if order.symbol in shares_per_symbol:
                shares_per_symbol[order.symbol] += order.num_of_shares
            else:
                shares_per_symbol[order.symbol] = order.num_of_shares

            if shares_per_symbol[order.symbol] > 0:
                portfolio.holdings_per_symbol[order.symbol] = shares_per_symbol[order.symbol] * price
	    
            portfolio.cash_amount = portfolio.cash_amount - (order.num_of_shares * price)

	elif order.order_type == 'Sell':
            
            if order.symbol in shares_per_symbol:
                shares_per_symbol[order.symbol] -= order.num_of_shares
                portfolio.holdings_per_symbol[order.symbol] = shares_per_symbol[order.symbol] * price
            else:
                print 'shorting'
                shares_per_symbol[order.symbol] = -(order.num_of_shares)

            
            portfolio.cash_amount = portfolio.cash_amount + (order.num_of_shares * price)

        return portfolio



def main():

	initial_sum = int(sys.argv[1])
	orders_file = sys.argv[2]
	values_file = sys.argv[3]

	keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

        p = Portfolio(initial_sum, 0)

	fund_daily_returns = {}

	orders_dict_by_date = defaultdict(list)
	orders_dict_by_symbol = defaultdict(list)
        shares_per_symbol = {}

	reader = csv.reader(open(orders_file, 'rU'), delimiter=',')

	# Scan the CSV file and store are relevant informaton
	for row in reader:
		year = int(row[0])
		month = int(row[1])
		date = int(row[2])
		symb = row[3]
		order_type = str(row[4])
		shares = int(row[5])

		full_date = dt.datetime(year, month, date, 16)

		order = Orders(full_date, symb, order_type, shares)

		orders_dict_by_date[order.full_date].append(order)
		orders_dict_by_symbol[order.symbol].append(order)
		#order.print_order()
		#print order.full_date

	dates_list = sorted(orders_dict_by_date)
	first_date = dates_list[0]
	last_date = dates_list[len(dates_list) - 1]

	symbols_list = sorted(orders_dict_by_symbol)
	num_symbols = len(symbols_list)

	time_of_day = dt.timedelta(hours=16)
	timestamps = du.getNYSEdays(first_date, last_date, time_of_day)

	symbol_data_obj = da.DataAccess('Yahoo', cachestalltime=0)
	symbol_data = symbol_data_obj.get_data(timestamps, symbols_list, keys)

	#print symbol_data[3]['AAPL'][first_date]
	
	
        delta = dt.timedelta(days=1)
        d = first_date
        last_return = 0
        todays_return = 0
        for idx in range(len(timestamps)):
            d = timestamps[idx]
            if d in orders_dict_by_date:
                for o in orders_dict_by_date[d]:
                    p = execute_order(o, shares_per_symbol, symbol_data, p)
            else: 
                for symb in shares_per_symbol:
                    if shares_per_symbol[symb] > 0:
                        p.holdings_per_symbol[symb] = shares_per_symbol[symb] * symbol_data[3][symb][timestamps[idx]]


            fund_daily_returns[d] = p.total_calc()


        writer = csv.writer(open(values_file, 'wb'), delimiter=',')
        for d in sorted(fund_daily_returns):
            row_to_enter = [d.year, d.month, d.day, fund_daily_returns[d]]
            writer.writerow(row_to_enter)



if __name__ == "__main__":
	main()


