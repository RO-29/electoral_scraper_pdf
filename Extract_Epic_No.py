from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import re
import csv
from bs4 import BeautifulSoup
import pdb
import re

"""We convert our Pdf to html with the help of pdfMiner,then search for specific spans containig our 
    epic_no by apllying a pattern over them.. epic_no either starts with ANB|GLT|UP in this specifc pdf
    and span which contains such epic no has it's {style="font-family: AAAAAC+Arial; font-size:10px"sss}
    we use this info to extract all the epic_no.

    EPIC_NO have it's all font AAAAC+ARIAL,i.e we could easily extract it.. similarly all the other elements(name,age,gender etc) have its
    own font which is helpful for extraction

    We could have easily extracted all the other info from this converted html only but due to the broken encoding
    we have only extracted the epic_no so that to reconstruct the info by inputting this no in EC Website!
"""

def convert_pdf_to_html(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    maxpages = 0 
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str

res = convert_pdf_to_html('data.pdf')

#print res
soup = BeautifulSoup(res,'lxml')
epic_nos = soup.find_all('span',{'style':"font-family: AAAAAC+Arial; font-size:10px"})

pattern = re.compile('^[ANB|UP|GLT]')
result_epic= list()

for no in epic_nos:
    if pattern.match(str(no.text)):
        #In Some Epic_No ,,Age is also bundelled along in same span  ..i.e split on white space
        result_epic.append(str(no.text).split(' ')[0])

print result_epic