import requests
from bs4 import BeautifulSoup
import urllib
import pdb
import csv
import unicodecsv
from cStringIO import StringIO
from global_var import *
from multiprocessing.dummy import Pool as ThreadPool



#This function builds our voter Repository
def write_to_csv(data,outfile,epicno=None):
	if data == 'No Match Found':
		result= list()
		result.append('NOT FOUND')
		result.append('EpicNo--')
		result.append(epicno)
	else:
		#convert the final html output to BeautifulSoup object
		soup = BeautifulSoup(data,'lxml')

		#this tbale with id='gvSearchResults' contains our result
		table = soup.find('table',{'id':'gvSearchResult'})
		rows = table.findChildren('tr')
		result= list()
		for row in rows:
			cells = row.findChildren('td')
			i=0
			for cell in cells:
				#since we don't need data for 4 previous cell ,i.e extra data provided by ec website
				if(i<4):
					i+=1
					continue

				value = cell.string
				#for hindi data,it was a pain lot of pain!!
				try:
				   #print value.encode('ISO-8859-1')
				   result.append(value.encode('ISO-8859-1').encode('utf-8'))
				except:
				   #print value
				   result.append(value)
				#print value.encode('ISO-8859-1')
				i+=1

	#Finally appending our extracted result to our output csv, i.e our voters repo
	resultFile = open(outfile,'ab+')
	f = StringIO()
	wr = unicodecsv.writer(resultFile, dialect='excel')
	wr.writerow(result)
	print result


#Extarct Form hidden Values identofied by their Id's.. return a list of Values
def extract_form_hiddens(soup):
	viewstate = soup.select("#__VIEWSTATE")[0]['value']
	eventvalidation = soup.select("#__EVENTVALIDATION")[0]['value']
	viewstategen = soup.select("#__VIEWSTATEGENERATOR")[0]['value']
	return [eventvalidation,viewstate,viewstategen]

def EpicNo_Search(EpicNo):
	global headers,formData,url

	#This Intermediate requests are made to get the eventvalidation,viewstae and viewstateGen Token
	session = requests.session()
	res = session.get(url,headers=headers)
	soup = BeautifulSoup(res.text,'lxml')
        #print 'res1-'+str(res)
	formData['__EVENTVALIDATION'],formData['__VIEWSTATE'],formData['__VIEWSTATEGENERATOR'] = extract_form_hiddens(soup)
	#.set_trace()
	formData['ddlDistricts'] ='--Select--'
	formData['RdlSearch'] = '1'
	formData['__EVENTTARGET']='RdlSearch$1'
	res = session.post(url,urllib.urlencode(formData), headers=headers)
	#print 'res2-'+str(res)
	soup = BeautifulSoup(res.text,'lxml')
	#Gets Token for District
	formData['__EVENTVALIDATION'],formData['__VIEWSTATE'],formData['__VIEWSTATEGENERATOR'] = extract_form_hiddens(soup)
	formData['__EVENTTARGET']= 'ddlDistricts'
	formData['ddlDistricts']= '67'
	res = session.post(url,formData, headers=headers)
	#print 'res3'+str(res)
	soup = BeautifulSoup(res.text,'lxml')

	#for getting tokens for AC and districts
	formData['__EVENTVALIDATION'],formData['__VIEWSTATE'],formData['__VIEWSTATEGENERATOR'] = extract_form_hiddens(soup)
	formData['ddlACs']='276'
	formData['__EVENTTARGET']= 'ddlAcs'
	res = session.post(url,formData, headers=headers)
	#print 'res4'+str(res)
	soup = BeautifulSoup(res.text,'lxml')

	"""Final Request to get the voter info,District 67 indicates faizabad and AC-Assembly
		Constituency 276 indicates Goishajganj... EpicNo is the unique no of every Voter
	"""
	formData['__EVENTVALIDATION'],formData['__VIEWSTATE'],formData['__VIEWSTATEGENERATOR'] = extract_form_hiddens(soup)
	formData['ddlACs']='276'
	formData['ddlDistricts']='67'
	formData['__EVENTTARGET']= ''
	formData['txtEPICNo']=EpicNo
	formData['Button1']= 'Search'
	res= session.post(url,formData, headers=headers)
	#print 'res5-'+str(res)

	if 'No Match Found' in res.text:
		write_to_csv('No Match Found','output.csv',epicno=EpicNo)
	else:
		write_to_csv(res.text.encode('utf-8'),'output.csv')


#We make 4 parrallel requests to Ec website for faster result consolidation,It's like Map-Reduce() 
pool = ThreadPool(4)
pool.map(EpicNo_Search, data_search)
