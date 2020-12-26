# import libraries
import csv
import pandas as pd
from difflib import SequenceMatcher

internet_ipo_path = 'Internet-IPOs.csv'
sentiment_path = 'Sentiment/company_sentiment_ticker.csv'
destination = 'Internet-Sentiment.csv'

# read in internet ipo csv file as dictionary
def makeInternetDict():
	reader = csv.reader(open(internet_ipo_path, 'r'))
	d = {}
	for row in list(reader)[1:]:
		ticker, name = row[3], row[0]
		d[ticker] = name
	return d

# write whether or not company is internet ipo to sentiment csv file
# 1 = is internet IPO, 0 = not internet IPO
def internetIPOMatch():
	internetDict = makeInternetDict()

	df = pd.read_csv(sentiment_path) # read in sentiment file
	df['internet'] = 0
	for index, row in df.iterrows():
		com_name, ticker = row['Name'], row['ticker']
		if ticker in internetDict: # check if company is internet IPO
			s = SequenceMatcher(None, internetDict[ticker].lower(),
								com_name.lower()).ratio()
			if s >= 0.65: # above 65% similarity between company names
				df.loc[index, 'internet'] = 1
	df.to_csv(destination, index=False, header=True)

internetIPOMatch()