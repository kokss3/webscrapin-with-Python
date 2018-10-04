import requests as req
from bs4 import BeautifulSoup #as soup
from bs4.dammit import EncodingDetector
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
	encoding = EncodingDetector.find_declared_encoding(data.content, is_html=True)
	
	#get HTML data
	pageData = BeautifulSoup(data.content, 'lxml', from_encoding=encoding)
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
	page_name1 = page_name1.replace("  "," ")

	if not(page_name1.find('Page ') == -1 ):
		page_number = int(page_name1[page_name1.find('Page ')+5:])
	else:
		page_number = page_number + 1
		page_name1 = page_name1 + ' - Page ' + str(page_number)
		page_name1 = page_name1.replace(' - - ',' - ')

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