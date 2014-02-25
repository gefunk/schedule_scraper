from datetime import datetime as dt	
from bs4 import BeautifulSoup
import re, sys
import urllib2
import pprint
    
class PageParser():    
    
    # pass in the url to the constructor
    def __init__(self, url):
        print "URL init {0}".format(url)
        self.url = url
        response = urllib2.urlopen(url)
        html = response.read()
        self.soup = BeautifulSoup(html)
        self.currentports = None
        self.page_data = []
    
    def parse(self):
        schedule_table = self.soup.find("table", {"class" : "f13tabn1"})
        
        for row in schedule_table.findAll('tr'):
            # check if it is a port row
            if row.findAll("td", class_="f09tilb1", limit=1):
                self.parse_ports_row(row)
            elif row.findAll("td", class_="f09rown1", limit=1) or row.findAll("td", class_="f09rown2", limit=1):
                self.page_data.append(self.parse_voyage_row(row))
                
        return self.page_data
        
    
    
    def parse_ports_row(self, portsoup):
        # skip the first row, because it is a spacer
        ports = portsoup.findAll('td')
        self.currentports = []
        for port in ports[1:]:
            port_str = port.string.strip()
            self.currentports.append(port_str)
    
    """
        Parse out an individual voyage row
    """
    def parse_voyage_row(self, rowsoup):
        
        data = {}
        
        cols = rowsoup.findAll('td')
        # get text out from this: MAERSK DRYDEN 346S
        raw_ship_voy = cols[0].string.strip().split()
        # the last string will be the voyage
        data["voyage"] = raw_ship_voy[-1]
        data["vessel"] = " ".join(raw_ship_voy[:-1])
        data['url'] = self.url
        data['scrape_date'] = dt.now()
        
        data['ports'] = []
        
        for index, datecol in enumerate(cols[2:]):
            dates = self.parse_date(datecol)
            if dates:
                # based on column, get the port
                data['ports'].append({"port": self.currentports[index], "eta": dates["eta"], "etd": dates["etd"]})
                
        return data
        
    
    
    """
        Parse out date from html
    """
    def parse_date(self, datesoup):
        eta = None
        etd = None
        
        date_str = []
        for text in datesoup.stripped_strings:
            date_str.append(text)
        
        # Parse out eta
        try:
            eta = dt.strptime(date_str[0]+"/"+str(dt.now().year), "%m/%d/%Y")
        except ValueError as e:
            try:
                found = re.findall('[0-1][0-9]/[0-3][0-9]', " ".join(datesoup.stripped_strings))
                if len(found) > 0:
                    date_str = found[0]
                    eta = dt.strptime(date_str+"/"+str(dt.now().year), "%m/%d/%Y")
                else:
                    raise ValueError
            except ValueError as e:
                pass
            
        
        # Parse out etd
        try:
            etd = dt.strptime(date_str[1]+"/"+str(dt.now().year), "%m/%d/%Y")
        except ValueError as e:
            if eta is not None:
                etd = eta
            
        if eta is not None:
            return {"eta": eta, "etd": etd}
        else:
            return None
            
            
#page_parser = PageParser("http://www.shipmentlink.com/tvs2/download_txt/AAE_S.html")
#print page_parser.parse()