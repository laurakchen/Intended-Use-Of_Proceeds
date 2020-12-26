# Import libraries
import csv
import re # regular expressions
from pandas import DataFrame


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

# c1 = Acquisitions
# c2 = Financing Transactions
# c3 = Growth Investment
# c4 = Production Investment
categories = ['c1', 'c2', 'c3', 'c4']


# create dictionary of categories and wanted words
def createDictionary(categories):
	# create keys of dictionary
	wordDict = {}
	simpleDict = {}
	wordSet = set()
	for category in categories:
		wordDict[category] = {}

	# create dictionary from csv file with counts set to 0
	path = '/Users/laurachen/Desktop/FinProject/dictionary.csv'
	f = open(path)
	csv_f = csv.reader(f)
	for row in list(csv_f)[1:]:
		row = row[0].split("\t")
		wordDict[row[1]][row[0]] = 0 #row[1]=category, row[0]=word
		wordSet.add(row[0])
		simpleDict[row[0]] = 0
	return wordDict, wordSet, simpleDict


# textual analysis of IPO prospectus
def analyzeText():
	categoryDict, wordSet, simpleDict = createDictionary(categories)
	wordDict = simpleDict
	wordLength, total, averageList = 0, 0, []
	names = ['Name', 'Filing Date', 'Word Length', 'c1', 'c2', 'c3', 'c4']
	companies = {key: [] for key in names}
	words = {'Name': [], 'Filing Date': []}
	for key in simpleDict:
		words[key] = []
	path = '/Users/laurachen/Desktop/FinProject/CompanyInfoNew.csv'
	destination = '/Users/laurachen/Desktop/FinProject/IPO_Stats_2.csv'
	dictDestination = '/Users/laurachen/Desktop/FinProject/Dictionary_Stats_2.csv'
	f = open(path)
	csv_f = csv.reader(f)

	for row in list(csv_f)[1:]:
		text = row[6].lower() # make text lowercase
		text = re.sub(r"[-,\"@\'?\.$%_\d]", "", text, flags=re.I)
		text = re.sub(r"\s+", " ", text, flags=re.I) # rid of multiple spaces
		twoWords = re.findall(r"\bworking capital\b|\bcapital expenditures\b|\bjoint ventures\b|\bresearch and development\b", text)
		for phrase in twoWords: # delete phrases from text
			text = re.sub(r"%s" % phrase, "", text)
			wordDict[phrase] += 1
			wordLength += 1
		text = re.split(r"\s+", text)
		for word in text: # update dictionary
			if word in wordSet:
				wordDict[word] += 1
			if word not in stopwords:
				wordLength += 1
		words['Name'] += [row[0]]
		words['Filing Date'] += [row[4]]
		for category in categoryDict: # compute proportion for each category
			for word in categoryDict[category]:
				categoryDict[category][word] = wordDict[word]
				total += wordDict[word]
				words[word] += [wordDict[word]]
			averageList += [str((total / wordLength) * 100)]
			total = 0

		newRow = [row[0], row[4], str(wordLength), averageList[0], averageList[1], averageList[2], averageList[3]]
		print(newRow)
		companies['Name'] += [newRow[0]]
		companies['Filing Date'] += [newRow[1]]
		companies['Word Length'] += [newRow[2]]
		companies['c1'] += [newRow[3]]
		companies['c2'] += [newRow[4]]
		companies['c3'] += [newRow[5]]
		companies['c4'] += [newRow[6]]
		wordLength, averageList, total = 0, [], 0 # reset
		for word in simpleDict.keys():
			wordDict[word] = 0

	# export company text stats to csv file
	df = DataFrame(companies, columns=names)
	df.to_csv(destination, index=None, header=True)

	# export dictionary words stats to csv file
	cols = ['Name', 'Filing Date']
	for word in simpleDict.keys():
		cols += [word]
	wordDf = DataFrame(words, columns=cols)
	wordDf.to_csv(dictDestination, index=None, header=True)

analyzeText()