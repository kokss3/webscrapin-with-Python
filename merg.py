import os
from pdfrw import PdfReader, PdfWriter
from collections import OrderedDict
from datetime import datetime
from tqdm import tqdm

currentFolder = os.getcwd()
merger = PdfWriter()
outFile = input("Insert name of file: ")

#print started time
print('Started time:')
print(datetime.now())

#generate list of present PDFs
pdffiles = [os.path.join(name)
             for root, dirs, files in os.walk(currentFolder)
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
di2=OrderedDict(sorted(di.items()))

counter=0
#iterate and merge pdfs 
for k, v in tqdm(di2.items()):
	merger.addpages(reversed(PdfReader(v).pages))
	merger.write(str(outFile) + '.pdf')



#print started time
print('Stop time:')
print(datetime.now())
print('Done!')