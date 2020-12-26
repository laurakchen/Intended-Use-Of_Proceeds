# import libraries
import csv
import pandas as pd
from difflib import SequenceMatcher

internet_sentiment_path = 'Internet-Sentiment.csv'
consolidated_file = 'IPO_Fee/Consolidated_IPO_Final_Text_copy.csv'
destination = 'IPO_Fee/Consolidated_IPO_v1.xlsx'

# merge internet sentiment file with consolidated file
def mergeData():
	internet_df = pd.read_csv(internet_sentiment_path) # read in internet sentiment file
	internet_df.rename(columns={'Filing Date': 'Sentiment_Filing_Date',
								'Name': 'Sentiment_Name'}, inplace=True)
	consolidated_df = pd.read_csv(consolidated_file, sep=",")
	consolidated_df.drop(['All Managers', "Managers.1", "All Managers.1", "Managers",
						  "Lead Manager"], axis=1, inplace=True)
	new_df = pd.merge(consolidated_df, internet_df, how='inner',
					  left_on=['ticker', 'Match Name'],
					  right_on=['ticker', 'Sentiment_Name'])
	print(new_df.shape)
	new_df.to_excel(destination, index=False, header=True)


mergeData()