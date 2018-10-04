from PyPDF3 import PdfFileWriter, PdfFileReader, PdfFileMerger
import os
import tqdm
import sys
from collections import OrderedDict
import win32file
import fitz

win32file._setmaxstdio(4096)
i = 0
print(win32file._getmaxstdio())

sys.setrecursionlimit(30000)

#with open('allPDFs.txt') as f:
#	pdflines = f.readlines()

pdffiles = [os.path.join(name)
             for root, dirs, files in os.walk(os.getcwd())
             for name in files
             if name.endswith((".pdf"))]

#get page number
def getPageNr(arg1):
		stro = str(arg1)
		stro=stro.replace('.pdf', '')
		listR = stro.split(' - ')
		listR[len(listR)-1] = listR[len(listR)-1].replace('-','')
		listR[len(listR)-1] = listR[len(listR)-1].replace('Page ','')
		pgNr=int(listR[len(listR)-1])
		return pgNr

#create dictionary and get whole list
di={}

#direct copy and create key from page number on back and value is original list
for string in pdffiles:
	di.setdefault(getPageNr(string),str(string))

	#sort it by keys
di2 = OrderedDict(sorted(di.items()))

pdffiles.clear()

for key,values in di2.items():
	pdffiles.append(values) 
	
out = fitz.open()
counter = 0
TOCs = []

pageAt1=0
pageAt2=0
pageAt3=0
pageAt4=0
pageAt3a=0
last1Book = '' 	
last2Book = ''
last3Book = ''

dic = {}
pdflines =[]

for a in pdffiles:
	pdflines.append(a.replace(' - ',' > ').replace('  ',' ').replace('.pdf',''))

	with open('out.txt', 'a') as file:
		file.write(a.replace(' - ',' > ').replace('  ',' ') + '\n')

if len(pdflines)==len(pdffiles):

	while counter<len(pdffiles):
		#### ukloni linkove
		doc = fitz.open(pdffiles[counter])
		
		grr = doc[len(doc)-1]
		sss = grr.getLinks()
		for l in sss:
			#print(l)
			grr.deleteLink(l)

		out.insertPDF(doc, to_page=(len(pdffiles)-1))

		toc = pdflines[counter].replace('\n','').replace('  ',' ').split(' > ')
		del toc[-1]

		first1Book = toc[0]
		first2Book = toc[1]
		first3Book = ''
		title = ''
		sizeOfBookmark = len(toc)

		if sizeOfBookmark>3:	
			first3Book = toc[2]
			title = toc[3]
		else:
			title = toc[2]

		if not first1Book == last1Book:
			pageAt1 = counter + 1
			TOCs.append([1, (first1Book), pageAt1])
			last1Book = first1Book 	

		if not first2Book == last2Book:
			pageAt2 = counter + 1
			TOCs.append([2, (first2Book), pageAt2])
			last2Book = first2Book

		#if there is 4-row bookmark, process it
		if sizeOfBookmark>6:
			if not first3Book == last3Book:
				pageAt3 = counter + 1
				TOCs.append([3, (first3Book), pageAt3])
				last3Book = first3Book

			#add 4th title
			pageAt4 = counter + 1
			TOCs.append([4, (title), pageAt4])

		#it is 3-row bookmark
		else:
			pageAt3a = counter + 1
			TOCs.append([3, (title), pageAt3a])		
			
		counter +=1

	out.setToC(TOCs)
	out.save(os.path.basename(os.getcwd())+'.pdf')
	out.close()
else:
	print('Not right')
