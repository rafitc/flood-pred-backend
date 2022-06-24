#This will not run on online IDE
import requests
from bs4 import BeautifulSoup

URL = "https://www.imdtvm.gov.in/index.php?option=com_content&task=view&id=24&Itemid=38"
r = requests.get(URL)


soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib
soup.prettify()


table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="Table1") 
rows = table.findAll(lambda tag: tag.name=='tr')
print(table)