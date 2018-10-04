import os
import tqdm
import sys
from collections import OrderedDict
import win32file
import fitz

#find position of full title
def getFullTitle(textSearch):
	k=0
	c = True
	#iterate through whole text and find position of title 
	while c == True:
			
		if not textSearch[k].find(' > ') > 0:
			c = True
			k += 1
		else:
			c = False
	rightTitle = textSearch[k]
	return rightTitle.split(' > ')

#remove Links in page
def removeLINK(rawDoc):
	g = 0
	#iterate through pages 
	while g < rawDoc.pageCount: 
		
		#load individual page
		grr = rawDoc.loadPage(g)
		
		#form a list of dicts of links
		sss = grr.getLinks()
			
		#tierate through list	
		for l in sss:
			
			#delete specific link dict
			grr.deleteLink(l)

		g += 1

	return rawDoc

#get list of files and sort the out based on '... - Page XXXX.pdf' extension
def getOrederedList():

	#get page number
	def getPageNr(arg1):
		stro = str(arg1)
		stro=stro.replace('.pdf', '')
		listR = stro.split(' - ')
		listR[len(listR)-1] = listR[len(listR)-1].replace('-','')
		listR[len(listR)-1] = listR[len(listR)-1].replace('Page ','')
		pgNr=int(listR[len(listR)-1])
		return pgNr

	pdffiles = [os.path.join(name)
	             for root, dirs, files in os.walk(os.getcwd())
	             for name in files
	             if name.endswith((".pdf"))]

	#create dictionary and get whole list
	di={}

	#direct copy and create key from page number on back and value is original list
	for string in pdffiles:
		di.setdefault(getPageNr(string),str(string))

	#sort it by keys
	di2 = OrderedDict(sorted(di.items()))

	#remove old stuff
	pdffiles.clear()

	#fill new values
	for key,values in di2.items():
		pdffiles.append(values) 
		
	return pdffiles

#produce TOC list
#returns list of list
def prepareTOC(position, currentTitle, placePage):
	tocList = [position + 1, currentTitle, placePage]
	#print(tocList)
	return tocList

out = fitz.open()
tocList = []
lastTitle = [None,None,None,None, None,None,None,None]
page = 0
skipping = 1
size = getOrederedList()

for ss in size:
	doc = fitz.open(ss)
	stepsToSkip = doc.pageCount
	openPDF = doc.loadPage(0)
	raw = openPDF.getText("text")
	raw = raw.split('\n')

	titleList = getFullTitle(raw)

	#create toc list
	i = 0
	isDifferent = False

	#ovdje ide dio koji puni listu iza teksta
	for singleTitle in titleList:
				
		if singleTitle != lastTitle[i]:
			isDifferent = True

		if isDifferent:
			tocList.append(prepareTOC(i, singleTitle, skipping))
			isDifferent = True

		else:
			isDifferent = False


		lastTitle[i] = singleTitle
		
		i+= 1	
	
	while i < 8:
		lastTitle[i] = None
		i += 1
	
	doc = removeLINK(doc)

	out.insertPDF(doc)
	skipping += stepsToSkip
	page += 1

#put tocList
out.setToC(tocList)
out.save(os.path.basename(os.getcwd())+'.pdf')
out.close()