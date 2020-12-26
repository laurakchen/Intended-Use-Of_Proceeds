# Import libraries
import requests
import time
import csv
from bs4 import BeautifulSoup
from pandas import DataFrame


startYr = 1997
endYr = 2019
startMonth = 0o1  # for python 3.6, use prefix 0o for single digits
endMonth = 12
stopDate = [2019, 0o7] # only need to change stopDate and endYr

# return list of company urls from start year to end year
def getCompany():
	breakInnerLoop = False
	result = []
	for year in range(startYr, endYr + 1):
		for month in range(startMonth, endMonth + 1):
			if [year, month] == stopDate:
				breakInnerLoop = True
				break
			url = 'https://www.nasdaq.com/markets/ipos/activity.aspx?tab=pricings&month=' \
				  + '%d-%d' % (year, month)
			response = requests.get(url)
			soup = BeautifulSoup(response.text, 'html.parser')
			companyNum = 0
			found = soup.find(id='two_column_main_content_rptPricing_company_'+ str(companyNum))

			# get links of IPOs
			while found != None:
				getLink = found.attrs['href']
				result += [getLink]
				companyNum += 1
				found = soup.find(id='two_column_main_content_rptPricing_company_'+ str(companyNum))
		if breakInnerLoop:
			break
	return result



# return list containing information of IPO
def getInfo(url):
	# Set the URL
	fullUrl = url + '?tab=financials'

	# Connect to the URL
	response = requests.get(fullUrl)

	# Parse HTML and save to BeautifulSoup object
	soup = BeautifulSoup(response.text, "html.parser")
	finding = True
	linkNum = 0
	pageNum = 1
	form, filingDate, downloadUrl = [], [], []
	wantedForm = '424B'

	while finding:
		found = soup.find(id='two_column_main_content_rpt_filings_fil_view_' + str(linkNum))
		if found == None: # account for new pages in filing forms
			pageNum += 1
			url = fullUrl + '&fpage=' + str(pageNum)
			response2 = requests.get(url)
			soup = BeautifulSoup(response2.text, 'html.parser')
			linkNum = 0
			found = soup.find(id='two_column_main_content_rpt_filings_fil_view_' + str(linkNum))
		if found == None: # check if no wanted forms found
			return [[], [], [], []]
		body = found.find_parent('tr')
		info = body.select("body td")
		name = info[0].text
		if wantedForm in info[1].text and linkNum >= 0:
			form += [info[1].text]
			filingDate += [info[2].text]
			downloadUrl += ['https://www.nasdaq.com' + info[3].find('a').attrs['href']]
		elif wantedForm not in form:
			break
		linkNum += 1
	return [name, form, filingDate, downloadUrl]


# return text of Use of Proceeds section of IPO
def getUop(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	if soup.find('pre') == None: # if there is no Use of Proceeds section
		return None
	text = soup.find('pre').text
	return text


# write company information to csv file
def infoToCsv():
	# change destination and form as needed
	destination = '/Users/laurachen/Desktop/FinProject/CompanyInfo/CompanyInfo' + \
				  '%d-%d_%d-%d.csv' % (startYr, startMonth, endYr, endMonth)
	wantedForm = '424B'
	forms = getCompany()
	companies = {'Name': [], 'Form': [], 'Filing Date': [], 'Overview Url': [],
				 'Form Url': [], 'Use of Proceeds Url': [], 'Use of Proceeds': []}
	for url in forms:
		info = getInfo(url)
		print(info)
		if info[1] != [] and wantedForm in info[1][0]:
			for i in range(len(info[1])):

				companies['Name'] += [info[0]]
				companies['Overview Url'] += [url]
				companies['Use of Proceeds Url'] += [url]
				companies['Form'] += [info[1][i]]
				companies['Filing Date'] += [info[2][i]]
				companies['Form Url'] += [info[3][i]]
				companies['Use of Proceeds'] += [getUop(url)]

		time.sleep(4) # pause code for 4 sec

	df = DataFrame(companies, columns=['Name', 'Overview Url', 'Use of Proceeds Url',
									   'Form', 'Filing Date',
									    'Form Url', 'Use of Proceeds'])
	df.to_csv(destination, index=None, header=True)



# get initial IPO prospectus and export as csv file
def getInitialIPO():
	result = []
	startY = 1997
	stopY = 2019
	startM = 0o1
	endM = 0o6
	cycle = 0

	with open('/Users/laurachen/Desktop/FinProject/IPO_File.csv', 'w') as file:
		writer = csv.writer(file, dialect='excel')
		for year in range(startY, stopY + 1):
			while cycle != 2:
			# cycle 0 = Jan-June, cycle 1 = July-Dec
				path = '/Users/laurachen/Desktop/FinProject/CompanyInfo/CompanyInfo' + \
							  '%d-%d_%d-%d.csv' % (year, startM, year, endM)
				f = open(path)
				csv_f = csv.reader(f)
				for row in reversed(list(csv_f)):
					if row[0] != 'Name':
						if result == []:
							result += [row]
						elif result[-1][0] != row[0]:
							# only add IPO file info
							result += [row]
				if startM == 0o1: # change cycle months
					startM, endM = 0o7, 12
				else:
					startM, endM = 0o1, 0o6
				writer.writerows(result) # write result to csv file
				result = []
				cycle += 1
				print(year, startM, endM)
				if year == 2019:
					break
				if year == 1997 and startM == 0o1:
					break
			cycle = 0 # reset cycle


