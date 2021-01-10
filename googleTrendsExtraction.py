# import libraries
import os
import datetime
import numpy as np
import pandas as pd
import pytrends
import re
from pytrends.request import TrendReq
pytrend = TrendReq() #hl='en-US', tz=360, timeout=(10,25), retries = 1000, backoff_factor=0.2)
import time
import random


ipoPath = "~/desktop/FinProject/IPO_Fee/Consolidated_IPO_v1.xlsx"
df = pd.read_excel(ipoPath)
df['Match Name'] = df['Match Name'].apply(lambda x: re.sub(r"[-,\"@\'?\.$%_\d]", "", x, flags=re.I).lower())
df['Match Name'] = df['Match Name'].apply(lambda x: re.sub(r"\s+", " ", x, flags=re.I))
comNameList = df['Match Name'].tolist() # ipo company names as list
df['Issue Date'] = df['Issue Date'].apply(lambda x: datetime.datetime.strptime(x,'%m/%d/%y'))
dateList = df['Issue Date'].tolist() # ipo issue date as list


#once we have list of keywords
searches = comNameList
searchLen = len(searches)
groupkeywords = list(zip(*[iter(searches)]*1))
groupkeywords = [list(x) for x in groupkeywords]
searchAvail = [0]*searchLen # dummy var column for whether gtrend search volume is available
searchAvgLst = [None]*searchLen # search volume average norm for ipo's

i = 0
fails = 0
for ipo in groupkeywords:
	try:
		issueDate = str(dateList[i])[:10]
		if int(issueDate[:4]) < 2004: # gtrend data not available
			print("IPO before 2004", i)
			i += 1
			fails = 0
			continue
		prevMonthDate = str(dateList[i]-pd.DateOffset(months=1))[:10]
		pytrend.build_payload(ipo, cat = 784 & 1163 & 1138 & 1164 & 1165,
							  timeframe = prevMonthDate+" "+issueDate)
		data = pytrend.interest_over_time()

		fails = 0
	except:
		print("exception raised", i)
		fails += 1
		delay = 2**fails + .001*random.randrange(1,1000)
		time.sleep(delay)
		print("...backed off for " + str(delay) + " seconds")
		continue
		# pass #originally continued, let's see if words get skipped
	if not data.empty:
		data[ipo[0]] = data[ipo[0]]-data[ipo[0]].median()
		searchAvgLst[i] = data[ipo[0]].mean() # average search volume (normalized)
		searchAvail[i] = 1
		print("IPO WORKED!", i)
		time.sleep(2)
	else:
		print("NO DATA AVAILABLE", i)
	i += 1
	fails = 0
	time.sleep(2)


zippedLst = list(zip(comNameList, dateList, searchAvgLst, searchAvail))
newDf = pd.DataFrame(zippedLst, columns=['company_name', 'issue_date',
										 'search_vol_avg', 'search_avail'])
dest = "~/desktop/FinProject/googleTrendsFile_v1.xlsx"
newDf.to_excel(dest, index=False, header=True) # export to xlsx file



# test
# pytrend.build_payload(['ZULILY INC'], cat = 784 & 1163 & 1138 & 1164 & 1165 & 1159,
# 							  timeframe = '2013-10-14'+" "+'2013-11-14')
# data = pytrend.interest_over_time()
# print(data)
# med = data['ZULILY INC'].median()
# data['ZULILY INC'] = data['ZULILY INC']-med
# avg = data['ZULILY INC'].mean()
# print(data)
# print(med, avg)