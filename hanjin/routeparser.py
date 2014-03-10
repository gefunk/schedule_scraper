import urllib
import urllib2
import json
from datetime import datetime


class RouteParser():
    
    def __init__(self, url):
        self.url = url
        
    '''
    Get all the routes for these 2 continent codes
    '''
    def get_routes_by_continent(self, from_continent, to_continent):
        values = {'f_cmd' : '121',
                  'frm_conti_cd' : from_continent,
                  'to_conti_cd': to_continent}

        obj = json.loads(self.make_http_call(values))
        
        routes = []
        if 'list' in obj:
            for route in obj['list']:
                routes.append({"name":route['vslSlanNm'], "code": route['vslSlanCd']})
            
        return routes
    
    '''
    Get the port header for the sailing schedule table
    '''
    def get_port_heading(self, route_code):
        values = {'f_cmd' : '122','vsl_slan_cd' : route_code}
        jsonObj = json.loads(self.make_http_call(values))
        ports = []
        if 'list' in jsonObj:
            for port in jsonObj['list']:
                ports.append(port['portNm'].strip())
        return ports
    
    '''
    Get voyage, vessel, dates from sailing schedule table,
    '''
    def get_route(self, service, route_code, ports):
        values = {'f_cmd' : '123',
                   'page':'1',
                   "rows":"10000",
                   "sord":"asc",
                   'vsl_slan_cd' : route_code,
                   "_search":"false"}
        jsonObj = json.loads(self.make_http_call(values))
        
        data = []
        
        # for each row that we find in the sailing schedule table
        # we are going to create a voyage object with the vessel, voyage, and all the ports and dates
        if 'list' in jsonObj: 
            for row in jsonObj['list']:
            
                # convert all parameters to get url string
                get_url = ""
                for (key,val) in values.iteritems():
                    get_url += ("%s=%r&" % (key,val))
                get_url = get_url[:-1]
            
                # init voyage object with the standard information
                voyage = {
                    "carrier":"Hanjin", 
                    "url": self.url+"?"+get_url, 
                    "scrape_date":datetime.now(),
                    'vessel': row['vslNm'],
                    "service": service,
                    'voyage': row['skdVoyNo'],
                    'ports': []
                }

                # initialize ports table in voyage 
                for port in ports:
                    voyage['ports'].append({"port":port})
                
                # for each row that we found we 
                for key,value in row.items():
                    if ("arr" in key or "dep" in key) and "Cd" not in key and isinstance(value, basestring):
                        timeformat = "%Y-%m-%d %H:%M"
                        port_date = None
                        try:
                            port_date = datetime.strptime(value, timeformat)
                            # Figure out arrival or departure
                            column = self.get_two_digit_num_code(key)-1
                            # set arrival or departure based on key (arr or dep)
                            if 'arr' in key:
                                voyage['ports'][column]['eta'] = port_date
                            elif 'dep' in key:
                                voyage['ports'][column]['etd'] = port_date
                        except ValueError:
                            pass
                data.append(voyage)
                
        # clean out ports that don't have dates,
        # some ports in the table don't have dates, remove them from data
        for voyage in data:
            for port in voyage['ports']:
                if "eta" not in port and "etd" not in port:
                    voyage['ports'].remove(port)
        
        
        # all the data we were able to gather
        return data
        
    '''
    parse out 2 digit number code
    '''
    def get_two_digit_num_code(self, raw_string):
        raw_number = raw_string[-2:]
        number = None
        try:
            number = int(raw_number)
        except ValueError:
            print "Not a valid number : {0}, from String : {1}".format(raw_number, raw_string)
        
        return number 
    
    '''
    Helper function to encapsulate all HTTP communication
    GET or POST data to Hanjin Server
    '''
    def make_http_call(self, data=None):
        req = None
        if data:
            req = urllib2.Request(self.url, urllib.urlencode(data))
        else:
            req = urllib2.Request(self.url)
        response = urllib2.urlopen(req)
        return response.read()
        