from datetime import datetime as dt	
from bs4 import BeautifulSoup
import re
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
        self.vessels = {}
            
    def parse(self):
        schedule_table = self.soup.find("table", {"class" : "tblData"})
        # keep track of vessels in current row
        # the index of this will be 0-indexed from the second column (first vessel name)
        # e.g. <tr><td>Vessel</td><td>MAERSK LIMA</td><td>MAERSK LUZ</td>
        # would be [0] = MAERSK LIMA, [1] = MAERSK LUZ
        current_row_vessels = None
        # keep track of voyages in current row
        # same as above, 0-indexed from second column (first voyage number)
        current_row_voyages = None
        
        for row in schedule_table.findAll('tr'):
            
            # get all columns within this row
            cols = row.findAll('td')
            # if this condition is not met, disregard row
            if cols[0].get_text() is not None and len(cols[0].get_text()) > 0:
                # Vessel row
                if cols[0].string.strip() == "Vessel":
                    current_row_vessels = self.parse_vessels_from_row(cols)
                elif "Voyage" in cols[0].string.strip():
                    current_row_voyages = self.parse_voyages_from_row(cols, current_row_vessels)
                else:
                    # none of the other conditions match - this is a port row
                    port = cols[0].string.strip()
                    for index, col in enumerate(cols[1:]):
                        cell_text = "".join(col.get_text().split())
                        # check if this is not a blank cell, blank cell only has '-'
                        if len(cell_text) > 1:
                            current_vessel = current_row_vessels[index]
                            current_voyage = current_row_voyages[index]
                            if not port in self.vessels[current_vessel][current_voyage]:
                                self.vessels[current_vessel][current_voyage][port] = {}
                            # add dates for this vessel, voyage and port
                            self.vessels[current_vessel][current_voyage][port] = self.parse_dates(cell_text)

        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(self.vessels)
        return self.vessels
        #print "Vessels: {0}".format(self.vessels)


    # read voyages from rows
    def parse_voyages_from_row(self, cols, row_vessels):
        row_voyages = []
        # start index from second column, first column is the heading "Voyage Number"
        for index,col in enumerate(cols[1:]):
            voyage = col.string.strip()
            row_voyages.append(voyage)
            if not voyage in self.vessels[row_vessels[index]]:
                self.vessels[row_vessels[index]][voyage] = {} 
        return row_voyages

    # read vessels from rows
    def parse_vessels_from_row(self,cols):
        # keep track of vessels in current row
        row_vessels = []
        # start index from second column, first column is the word "Vessel"
        for col in cols[1:]:
            vessel = col.string.strip()
            row_vessels.append(vessel)
            if not vessel in self.vessels:
                self.vessels[vessel] = {}
        return row_vessels
    
    # Parse scell for all Possible HTML 
    def parse_date_cell(self, html):
        cell = BeautifulSoup(html)
        cell_text = "".join(cell.get_text().split())
        return cell_text
        
    # Parse date out of date str
    # string should be in 2 possible formats
    # 1: 30Jun-01Jul
    # 2: 07-07Feb
    def parse_dates(self, date_str):
        # split into 2 dates, format is always eta-etd
        dates = date_str.split('-')
        # parse out the day - get only digits
        etd_day = int(re.findall('\d+', dates[1])[0])
        eta_day = int(re.findall('\d+', dates[0])[0])
        # parse out the month, get only strings e.g.: Feb, Jan, Mar
        etd_month = re.findall("[a-zA-Z]+", dates[1])[0]
        eta_month = re.findall("[a-zA-Z]+", dates[0])
        # month is not always included for ETA, if not included set to etd month
        if len(eta_month) > 0:
            eta_month = eta_month[0]
        else:
            eta_month = etd_month
        # convert to date
        eta = dt.strptime(str(eta_day)+"/"+eta_month+"/"+str(dt.now().year), "%d/%b/%Y")
        etd = dt.strptime(str(etd_day)+"/"+etd_month+"/"+str(dt.now().year), "%d/%b/%Y")
        return {"eta":eta, "etd":etd}


#parser = PageParser("http://sailingschedules2.maerskline.com/MaerskSailingSchedulesCustomerWeb/CustomerWebServlet?ssaction=com.saf.ss.cust.action.route.ShowRoute&fromRegionID=2&toRegionID=21&liveworking=LIVE")
#parser.parse()
        