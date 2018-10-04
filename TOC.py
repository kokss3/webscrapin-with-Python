import os
from pdfrw import PdfReader, PdfWriter
from collections import OrderedDict
from datetime import datetime
from tqdm import tqdm
import xlsxwriter

currentFolder = os.getcwd()
merger = PdfWriter()
#outFile = input("Insert name of file: ")

#generate list of present PDFs
pdffiles = [os.path.join(name)
             for root, dirs, files in os.walk(currentFolder)
             for name in files
             if name.endswith((".pdf"))]

def getPart(arg1, position):
		stro = str(arg1)
		stro=stro.replace('.pdf', '')
		listR = stro.split(' - ')
		listR[position] = listR[position].replace('-','')
		listR[position] = listR[position].replace('Page ','')
		return listR[position]



#get page number
def getPageNr(arg1):
		stro = str(arg1)
		stro=stro.replace('.pdf', '')
		listR = stro.split(' - ')
		listR[len(listR)-1] = listR[len(listR)-1].replace('-','')
		listR[len(listR)-1] = listR[len(listR)-1].replace('Page ','')
		pgNr=int(listR[len(listR)-1])
		return pgNr

def getTitle(arg1):
		stro = str(arg1)
		stro=stro.replace('.pdf', '')
		listR = stro.split(' - ')
		listR[len(listR)-2] = listR[len(listR)-2].replace('-','')
		listR[len(listR)-2] = listR[len(listR)-2].replace('  ', ' ')
		pgTtl=str(listR[len(listR)-2])
		return pgTtl

#create dictionary and get whole list
di={}

#direct copy and create key from page number on back and value is original list
for string in pdffiles:
	li = list((getPart(string, 0), getPart(string, 1), getPart(string, 2), getTitle(string)))
	di.setdefault(getPageNr(string),li)

#sort it by keys
di2=OrderedDict(sorted(di.items()))

workbook = xlsxwriter.Workbook('data.xlsx')
worksheet = workbook.add_worksheet()

row = 2
col = 3
oldT0 = ''
oldT1 = ''
oldT2 = ''
oldT3 = ''
counter = 1
pageNR = 23
bold = workbook.add_format({'bold': True, 'font_name':'Times New Roman', 'font_size':8})
normal = workbook.add_format({'font_name':'Times New Roman', 'font_size':8})
#iterate and merge pdfs 
for key, value in tqdm(di2.items()):
	toPrint = False
	if not(oldT0 == value[0]):
		worksheet.write(row, col - 2, value[0], bold)
		row += 1
	if not(oldT1 == value[1]):
		worksheet.write(row, col - 1, value[1], bold)	
		row += 1
	if not(oldT2 == value[2]):
		worksheet.write(row, col, value[2], normal)	
		toPrint = True
    	#row += 1
	if not(oldT3 == value[3]):
       	#worksheet.write(row, col, value[3] + ' - ' + str(counter + 1))
		counter += 1
	if(toPrint):
		worksheet.write(row, col + 1, pageNR, normal)
		row += 1
    #else:
    	#worksheet.write(row, col, value[3])
    	#counter = 1
    					
    #worksheet.write(row, col + 1, pageNR)
	oldT0 = value[0]
	oldT1 = value[1]
	oldT2 = value[2]
	oldT3 = value[3]
    #row += 1
	pageNR += 1
    
workbook.close()

#print stop
print('Done!')