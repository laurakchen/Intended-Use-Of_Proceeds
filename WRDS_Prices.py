# import libraries
import csv
import pandas as pd
from pandas import DataFrame

# join stocks.csv and prices.csv together into one output file
def joinTables():
	columns = ['permno', 'permco', 'namedt', 'nameenddt', 'comnam', 'cusip', 'ticker', 'exchcd',
			   'begdat', 'begprc', 'date', 'prc']
	stocks = {key: [] for key in columns}
	stockPath = '/Users/laurachen/Desktop/FinProject/stocks.csv'
	pricePath = '/Users/laurachen/Desktop/FinProject/prices.csv'
	outputPath = '/Users/laurachen/Desktop/FinProject/stockPrices.csv'
	file = open(pricePath)
	csv_file = csv.reader(file)
	priceDict = {}
	for row in list(csv_file):
		permno = row[2]
		priceDict[permno] = [row[0], row[1], row[3], row[4]]

	f = open(stockPath)
	csv_f = csv.reader(f)

	for row in list(csv_f)[1:]:
		stockPermno = row[0]
		stockDate = row[2]
		if stockPermno in priceDict:
			if stockDate == priceDict[stockPermno][1]:
				for i in range(len(row)):
					stocks[columns[i]] += [row[i]]
				stocks['begdat'] += [priceDict[stockPermno][0]]
				stocks['begprc'] += [priceDict[stockPermno][1]]
				stocks['date'] += [priceDict[stockPermno][2]]
				stocks['prc'] += [priceDict[stockPermno][3]]

	df = DataFrame(stocks, columns=columns)
	df.to_csv(outputPath, index=None)


# match CRSP data to SDC data using CUSIP number and add new columns to IPO dataset
def matchCRSP():
	ipoPath = '/Users/laurachen/Desktop/FinProject/IPO_Fee/Consolidated_IPO_Fee.xlsx'
	stockFile = '/Users/laurachen/Desktop/FinProject/stockPrices.csv'

	# convert ipo file to csv file
	# ipoFile = pd.read_excel(ipoPath, index_col=None)
	# ipoFile.to_csv('/Users/laurachen/Desktop/FinProject/IPO_Fee/Consolidated_IPO_Fee.csv', encoding='utf-8', index=False)
	ipoPath = '/Users/laurachen/Desktop/FinProject/IPO_Fee/Consolidated_IPO_Fee.csv'
	file = open(ipoPath)
	csv_file = csv.reader(file)
	stock_csv = open(stockFile)
	csv_stock_file = csv.reader(stock_csv)

	# get dictionary of all stocks
	stockDict = {}
	nameDict = {}
	tickerDict = {}
	for row in list(csv_stock_file)[1:]:
		cusipFull = row[5]
		if len(cusipFull) > 6:
			cusip = row[5][:6]
		else:
			cusip = cusipFull
		permno = row[0]
		comnam = row[4]
		ticker = row[6]
		begprc = row[9]
		prc = row[11]
		stockDict[cusip] = [permno, cusipFull, comnam, ticker, begprc, prc]
		nameDict[comnam] = [permno, cusipFull, comnam, ticker, begprc, prc]
		if ticker != None:
			tickerDict[ticker] = [permno, cusipFull, comnam, ticker, begprc, prc]

	# match CRSP data to SDC data
	columns = ['permno', 'cusip', 'comnam', 'ticker', 'begprc', 'prc']
	colDict = {key: [] for key in columns}
	for row in list(csv_file)[1:]:
		comnam = row[2].upper()
		ticker = row[5]
		if row[13] != None:
			if len(row[13]) > 6:
				cusip = row[13][:6]
			else:
				cusip = row[13]
		else:
			cusip = None
		if cusip != None and cusip in stockDict: # check that cusip and ticker match
			if ticker == stockDict[cusip][3]:
				i = 0
				for key in columns:
					colDict[key] += [stockDict[cusip][i]]
					i += 1
		else:
			for key in columns:
				colDict[key] += [None]
		# else:
		# 	if comnam in nameDict:
		# 		j = 0
		# 		for key in columns:
		# 			colDict[key] += [nameDict[comnam][j]]
		# 			j += 1
		# 			continue
		# 	elif ticker in tickerDict:
		# 		k = 0
		# 		for key in columns:
		# 			colDict[key] += [tickerDict[ticker][k]]
		# 			k += 1
		# 			continue
		# 	else:
		# 		for key in columns:
		# 			colDict[key] += [None]
	df = pd.read_csv(ipoPath)
	df = df.assign(permno = colDict['permno'], cusip = colDict['cusip'],
				   comnam = colDict['comnam'], ticker = colDict['ticker'],
				   begprc = colDict['begprc'], prc = colDict['prc'])
	newPath = '/Users/laurachen/Desktop/FinProject/IPO_Fee/Consolidated_IPO_Final.csv'
	df.to_csv(newPath, index=None)


# search for duplicate rows with same ticker symbol in consolidated IPO file
def searchDuplicateTicker():
	ipoPath = '/Users/laurachen/Desktop/FinProject/IPO_Fee/Consolidated_IPO_Final.csv'
	file = open(ipoPath)
	csv_file = csv.reader(file)

	tickerSet = set()
	for row in list(csv_file)[1:]:
		cusip = row[45]
		comnam = row[46]
		ticker = row[47]
		begprc = row[48]
		if ticker != None:
			if ticker in tickerSet:
				print(ticker, cusip, comnam, begprc)
				print("\n")
			else:
				tickerSet.add(ticker)

# search for duplicate rows with same permno in consolidated IPO file
def searchDuplicatePermno():
	ipoPath = '/Users/laurachen/Desktop/FinProject/IPO_Fee/Consolidated_IPO_Final.csv'
	file = open(ipoPath)
	csv_file = csv.reader(file)

	permnoSet = set()
	numDuplicates = 0
	for row in list(csv_file)[1:]:
		permno = row[44]
		cusip = row[45]
		comnam = row[46]
		ticker = row[47]
		begprc = row[48]
		if permno != None:
			if permno in permnoSet:
				print(ticker, cusip, comnam, begprc)
				print("\n")
				numDuplicates += 1
			else:
				permnoSet.add(permno)
	print(numDuplicates)

