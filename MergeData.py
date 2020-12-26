# Import Libraries
import requests
import time
import csv
import pandas as pd
from bs4 import BeautifulSoup
from pandas import DataFrame


# webscrape ticker symbol of companies from given year & month from NASDAQ IPO website
def getTicker(year, month):
	url = 'https://www.nasdaq.com/markets/ipos/activity.aspx?tab=pricings&month=' \
		  + '%d-%d' % (year, month)
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	companyNum = 0
	tickerDict = {}

	for tag in soup.div.find_all_next('td'):
		getName = tag.find(
			id='two_column_main_content_rptPricing_company_' + str(companyNum))
		getTicker = tag.find(
			id='two_column_main_content_rptPricing_symbol_' + str(companyNum))
		if getName != None:
			comnam = getName.contents[0]
		elif getTicker != None:
			if getTicker.contents != []:
				ticker = getTicker.contents[0]
			else:
				ticker = None
		elif str(year) in tag.contents[0]:
			date = tag.contents[0]
			filingYr = date[-1:-5:-1][::-1]
			tickerDict[comnam] = [ticker, filingYr]
			companyNum += 1
		if '\n' in tag.contents[0]:
			break
	return tickerDict

# write ticker symbols to csv file
def writeTickerToFile():
	stYr, stMo = 2019, 0o1 # start year and start month
	eYr, eMo = 2019, 0o6
	destination = '/Users/laurachen/Desktop/FinProject/Ticker_Files/Ticker_%d.csv' % stYr

	allTickers = {'comnam': [], 'ticker': [], 'filingYr': []}
	for yr in range(stYr, eYr + 1):
		for mo in range(stMo, eMo + 1):
			tickerDict = getTicker(yr, mo)
			for comnam in tickerDict:
				ticker = tickerDict[comnam][0]
				filingYr = tickerDict[comnam][1]
				allTickers['comnam'] += [comnam]
				allTickers['ticker'] += [ticker]
				allTickers['filingYr'] += [filingYr]
				print(comnam, ticker, filingYr)
			time.sleep(2) # pause code for 2 secs

	df = DataFrame(allTickers, columns=['comnam', 'ticker', 'filingYr'])
	df.to_csv(destination, index=None, header=True)


# compile all ticker files into one csv file
def compileTickers():
	destination = '/Users/laurachen/Desktop/FinProject/All_Tickers.csv'
	stYr, eYr = 1997, 2019
	allTickers = []

	with open(destination, 'w') as file:
		writer = csv.writer(file, dialect='excel')
		writer.writerows([['comnam', 'ticker', 'filingYr']])
		for yr in range(stYr, eYr + 1):
			tickerPath = '/Users/laurachen/Desktop/FinProject/Ticker_Files/Ticker_%d.csv' % yr
			f = open(tickerPath)
			csv_f = csv.reader(f)
			for row in list(csv_f)[1:]:
				allTickers += [row]
			writer.writerows(allTickers)
			allTickers = []


# append corresponding ticker symbols to IPO stats csv file
def appendTicker():
	ipoPath = '/Users/laurachen/Desktop/FinProject/IPO_Stats.csv'
	tickerPath = '/Users/laurachen/Desktop/FinProject/All_Tickers.csv'
	file = open(ipoPath)
	csv_file = csv.reader(file)
	tickerFile = open(tickerPath)
	ticker_csv = csv.reader(tickerFile)
	tickerDict = {}
	allTickers = []

	# create dictionary of all companies and their tickers/filing years
	for row in list(ticker_csv)[1:]:
		comnam, ticker, date = row[0], row[1], row[2]
		tickerDict[comnam] = [ticker, date]

	# match ticker symbol to company in IPO stats csv file
	for row in list(csv_file)[1:]:
		comnam, yr = row[0], row[1][-1:-3:-1][::-1]
		if comnam in tickerDict:
			if yr == tickerDict[comnam][1][-1:-3:-1][::-1]:
				allTickers += [tickerDict[comnam][0]]
			else: allTickers += [None]
		else: allTickers += [None]

	df = pd.read_csv(ipoPath)
	df = df.assign(ticker=allTickers)
	newPath = '/Users/laurachen/Desktop/FinProject/IPO_Stats_Final.csv'
	df.to_csv(newPath, index=None)


# match and merge text analysis to consolidated IPO csv file using ticker, company name, and date
def matchTextStatToIPO():
	textPath = '/Users/laurachen/Desktop/FinProject/IPO_Stats_Final.csv'
	ipoCopyPath = '/Users/laurachen/Desktop/FinProject/IPO_Fee/Consolidated_IPO_Final_Text.csv'
	destination = '/Users/laurachen/Desktop/FinProject/IPO_Fee/IPO_Text_Analysis.csv'
	textFile = open(textPath)
	text_csv = csv.reader(textFile)
	ipoFile = open(ipoCopyPath)
	ipo_csv = csv.reader(ipoFile)
	tickerDict = {}
	columns = ['Match Name', 'Match Date', 'Word Length', 'c1', 'c2', 'c3', 'c4']
	colDict = {key: [] for key in columns}

	# create dict of tickers and their company/filing years
	for row in list(text_csv)[1:]:
		ticker = row[7]
		if ticker != None:
			comnam = row[0]
			filingYr = row[1][-1:-3:-1][::-1]
			date = row[1]
			wordCount = row[2]
			c1, c2, c3, c4 = row[3], row[4], row[5], row[6]
			tickerDict[ticker] = [filingYr, comnam, date, wordCount, c1, c2, c3, c4]

	# match ticker to consolidated IPO csv file's tickers and merge text analysis info
	for row in list(ipo_csv)[1:]:
		ipoYear = row[48][-1:-3:-1][::-1]
		ipoTicker = row[47]
		if ipoTicker in tickerDict and ipoYear == tickerDict[ipoTicker][0]:
			i = 1
			for col in columns:
				colDict[col] += [tickerDict[ipoTicker][i]]
				i += 1
		else:
			for col in columns:
				colDict[col] += [None]

	df = DataFrame(colDict, columns = ['Match Name', 'Match Date', 'Word Length', 'c1', 'c2', 'c3', 'c4'])
	df.to_csv(destination, index=None, header=True)

	# df = pd.read_csv(ipoCopyPath)
	# df = df.assign(WordLength = colDict['Word Length'], c1 = colDict['c1'],
	# 			   c2 = colDict['c2'], c3 = colDict['c3'], c4 = colDict['c4'])
	# df.to_csv(destination, index=None)