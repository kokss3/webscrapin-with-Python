import requests as req
from bs4 import BeautifulSoup as soup
import os
import pdfkit
from PyPDF2 import PdfFileWriter, PdfFileReader
from pdfrw import PdfReader, PdfWriter
from collections import OrderedDict
from datetime import datetime
from tqdm import tqdm
import xlsxwriter
import urllib3


urllib3.disable_warnings()
url = input("Insert URL: \n")
page_number = 1
#url = 'https://workshop-manuals.com/bmw/3_series_e30/325i_m20_sal/1_service_information/0__maintenance_and_general_data/1_si__modified_change_intervals_e9x-m3-us/'
has_next = True
while has_next:
	data = req.get(url)

	#get HTML data
	pageData = soup(data.text, 'lxml')
	bodyR = pageData.find_all('td',{'style':'vertical-align:top;background-color:#FFFFFF;'})
	partR = bodyR[3]

	#remove script
	something_to_remove = partR.find('script')

	#body of html
	textR = str(partR).replace( u'â¢', u' ')
	textR = textR.replace(str(something_to_remove), '')

	#got page name of image
	header_H3 = partR.find_all('h3')
	part_of_out = header_H3[len(header_H3)-1].text
	page_name1 = part_of_out.replace(">","-")
	
	if not(page_name1.find('Page ') == -1 ):
		page_number = int(page_name1[page_name1.find('Page ')+5:])
	else:
		page_number = page_number + 1
		page_name1 = page_name1 + ' - Page ' + str(page_number)
		page_name1 = page_name1.replace(' - - ',' - ')
		#page_name1 = page_name1.replace('  ',' ')

	#search for background image link
	imgs = partR.find_all('img')
	links = [each.get('src') for each in imgs]
	base_link = 'https://workshop-manuals.com'
	image_link = links[0].strip()

	#generate background filename and extension
	out_link = base_link + (image_link)
	
	#override in HTML body link of image
	out_tank = textR.replace(image_link,out_link)
	
	#save background image
	fileName_png = page_name1 + ".png"
	with urllib3.PoolManager() as http:
	    r = http.request('GET', out_link)
	    with open(fileName_png, 'wb') as fout:
	        fout.write(r.data)

	#saved file html
	fileName_html = (page_name1 + (".html"))
	with open(fileName_html, 'w', encoding = 'utf-8-sig') as file:
	    file.write(out_tank)

	#make PDF filename with extension
	fileName_pdf = (page_name1 + (u".pdf"))
	
	#options for PDFkit
	options = {
    	'quiet': ''
    }

    #convert html to pdf
	pdfkit.from_file(fileName_html, fileName_pdf, options=options)
	
	#print name as success
	print(fileName_pdf)

	#to find next button
	novo = pageData.find('div',{'style':'text-align:center;'})
	body_pre = novo.find('p',{'style':'text-align:right;'})
	
	#get link assigned as Next
	body_pre_ps = body_pre.find('a', href=True, text='[NEXT PAGE]')

	#loop while there is next link
	if not body_pre_ps==None: 
		#print(body_pre_ps)
		url = body_pre_ps.get('href')
		has_next = True
	else:
		has_next = False
		print('done!')
		os.remove(fileName_html)
		os.remove(fileName_png)
		break  

	#remove HTML and Image
	os.remove(fileName_html)
	os.remove(fileName_png)

currentFolder = os.getcwd()
merger = PdfWriter()
outFile = os.path.basename(os.getcwd())

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

workbook = xlsxwriter.Workbook( str(outFile) + ' toc.xlsx')
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
worksheet.write(row-2, col , str(outFile), bold)	

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

merger = PdfWriter()
outFile = os.path.basename(os.getcwd())

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
print('Stop time. ')

