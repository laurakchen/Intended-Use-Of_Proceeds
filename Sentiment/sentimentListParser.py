# Import libraries
import csv
import re
import string
import pandas as pd
from os import listdir

sentiment_word_list_path = '/Users/laurachen/Desktop/FinProject/Sentiment/LM_SentimentWordLists.csv'
company_info_folder = '/Users/laurachen/Desktop/FinProject/CompanyInfo'
destination = '/Users/laurachen/Desktop/FinProject/Sentiment/company_sentiment.csv'
categories_csv_path = 'IPO_Stats_Final.csv'
destination_with_ticker = 'Sentiment/company_sentiment_ticker.csv'

stopwords = {'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
                       'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
                       'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
                       'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be',
                       'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'an',
                       'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by',
                       'for', 'with', 'about', 'between', 'into', 'through', 'during', 'before',
                       'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
                       'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
                       'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
                       'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can',
                       'just', 'should', 'now'}

# create dictionary of aggregated sentiment word lists by Loughran and McDonald
def createDict(listPath):
	# create keys of dictionary
	wordDict = {}
	path = listPath
	f = open(path)
	csv_f = csv.reader(f)
	for row in list(csv_f)[1:]:
		wordDict[row[0].lower()] = row[1] #row[1]= category, row[0]=word
	return wordDict

# parse through use of proceeds text and return % of sentiment for each category
def sentimentParser(filepath, sentimentDict):
	categories = ['negative', 'positive', 'uncertainty', 'litigious',
				  'strongmodal', 'weakmodal', 'constraining']
	colNames = ['Name', 'Filing Date', 'Word Length', *categories]
	companies = {key: [] for key in colNames}
	sentimentCountDict = {cat: 0 for cat in categories}
	wordLength = 0
	f = open(filepath, encoding="ISO-8859-1") # need this encoding or it'll throw utf-8 errors
	csv_f = csv.reader(f)

	for row in list(csv_f)[1:]:
		text = row[6].lower() # make text lowercase
		text = re.sub(r"[-,\"@\'?\.$%_\d]", "", text, flags=re.I)
		text = re.sub(r"\s+", " ", text, flags=re.I)  # rid of multiple spaces
		text = re.split(r"\s+", text)
		for word in text:
			if word in sentimentDict:
				sentimentCountDict[sentimentDict[word]] += 1
			if word not in stopwords:
				wordLength += 1

		for category in colNames[3:]: # compute proportion for each category
			prop = sentimentCountDict[category]/wordLength
			companies[category] += [prop]
		companies['Name'] += [row[0]]
		companies['Filing Date'] += [row[4]]
		companies['Word Length'] += [wordLength]
		# reset
		wordLength = 0
		sentimentCountDict = {cat: 0 for cat in categories}

	df = pd.DataFrame(companies, columns=colNames) # make into dataframe
	# df.to_csv(destination, index=False, header=True)
	return df

# calculate sentiment for each csv file in company info folder
def doAllFiles():
	categories = ['negative', 'positive', 'uncertainty', 'litigious',
				  'strongmodal', 'weakmodal', 'constraining']
	colNames = ['Name', 'Filing Date', 'Word Length', *categories]
	df = pd.DataFrame(columns=colNames)
	sentimentDict = createDict(sentiment_word_list_path)
	company_files = [f for f in listdir(company_info_folder)]
	for file in company_files:
		if file != ".DS_Store":
			sentiment_df = sentimentParser('CompanyInfo/'+file, sentimentDict)
			df = df.append(sentiment_df, ignore_index=True)
	# export dataframe to csv file
	print(df.shape[0]) # print number of rows
	df.to_csv(destination, index=False, header=True)

# add ticker column to sentiment csv file
def addTicker():
	sentiment_df = pd.read_csv(destination)
	categories_df = pd.read_csv(categories_csv_path)
	new_df = pd.merge(categories_df, sentiment_df, how='left',
					  left_on=['Name', 'Filing Date'],
					  right_on=['Name', 'Filing Date'])
	new_df.to_csv(destination_with_ticker, index=False, header=True)


# doAllFiles()
addTicker()