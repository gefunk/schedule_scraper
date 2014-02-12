import urllib2
from bs4 import BeautifulSoup

page_link = 'http://sailingschedules2.maerskline.com/MaerskSailingSchedulesCustomerWeb/CustomerWebServlet?ssaction=com.saf.ss.cust.action.route.ShowSchedule&routeID=382&format=html&liveworking=LIVE'


response = urllib2.urlopen(page_link)

html = response.read()
soup = BeautifulSoup(html)

print(soup.prettify())

