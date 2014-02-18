import urllib2
from pageparser import PageParser
from optparse import OptionParser
import sys, ConfigParser
from datetime import datetime as dt
from pymongo import MongoClient
from bson.objectid import ObjectId
from bs4 import BeautifulSoup
import pprint


# initialize config parser
config = ConfigParser.RawConfigParser()

    
def start():
    
    # mongo connection
    uri = config.get("mongodb", "uri")
    connection = MongoClient(uri)
    db = connection[config.get("mongodb", "db")]
    
    urls = get_schedule_urls()
    for url in urls:
        log = {"start": dt.now(), "url": url}
        parser = PageParser(url)
        schedules = parser.parse()
        for key in schedules:
            # find the vessel in the schedule collection
            # if it doesn't exist then create a new one
            vessel = {"vessel":key,"carrier":"Maersk"}
            if db.schedules_temp.find_one(vessel):
                vessel = db.schedules_temp.find_one(vessel)
            # format data for how we want to store it in mongo
            voyages = schedules[key]
            vessel['voyages'] = []
            for voyage in voyages:
                ports = []
                for port in voyages[voyage]:
                    port_data = voyages[voyage][port]
                    port_data['port'] = port
                    ports.append(port_data)
                vessel["voyages"].append({"voyage":voyage, "ports":ports})
            
            # this data is used to help diagnose issues
            vessel['url'] = url
            vessel['scrape_date'] = dt.now()
            # save only performs an update if the document exists
            # otherwise inserts new one
            db.schedules_temp.save(vessel)
        # log the fact that we scraped this schedule
        log['finish'] = dt.now()
        db.scrapelogs.insert(log)


def get_schedule_urls():
    
    js_url = 'http://sailingschedules2.maerskline.com/MaerskSailingSchedulesCustomerWeb/CustomerWebServlet?ssaction=com.saf.ss.cust.action.route.ShowRouteSelection&liveworking=LIVE'
    
    response = urllib2.urlopen(js_url)
    
    data = response.readlines()
    
    jsFunctionStr = '';
    # boolean to keep track of whether we are reading the js function or not
    readingFunction = False
    for line in data:
        # traverse javascript function to get the regionids to destination regions
        if line.find('switch( fromRegionID  )') > 0:
            readingFunction = True
            jsFunctionStr += line
        elif readingFunction and (line.find('default') > 0):
            break;
        elif readingFunction:
            jsFunctionStr += line


    #print "This is the jsFunctionStr {0}".format(jsFunctionStr)

    # dict to keep track of region relationship
    # Asia to North America
    # Asia to South America
    # etc...
    # stored as codes e.g. 2 - 103, 104
    # second link is an array
    regionRelations = []
    global regionDict
    regionDict = {}
    
    for line in jsFunctionStr.split('\n'):
        if line.find('case') > 0:
            origin_region_code = line.rsplit('\"')[1]
            # 2d array, the second array will contain all the destination codes for this origin code
            origin_array = [origin_region_code, []]
            regionRelations.append(origin_array)
        elif line.find('Option') > 0:
            origin_array = regionRelations[len(regionRelations) - 1]
            region_code = line.rsplit('\"')[3]
            region_name = line.rsplit('\"')[1]
            origin_array[1].append(region_code)
            regionDict[region_code] = region_name

    #print regionRelations
    #print regionDict

    url = 'http://sailingschedules2.maerskline.com/MaerskSailingSchedulesCustomerWeb/CustomerWebServlet?ssaction=com.saf.ss.cust.action.route.ShowRoute&fromRegionID={0}&toRegionID={1}&liveworking=LIVE'
    
    urls = []
    # generate URLs
    for region in regionRelations:
        for relation in region[1]:
            subUrl = url.format(region[0], relation)
            urls.append(subUrl)
            
    #urls = ['http://sailingschedules2.maerskline.com/MaerskSailingSchedulesCustomerWeb/CustomerWebServlet?ssaction=com.saf.ss.cust.action.route.ShowRoute&fromRegionID=3&toRegionID=2&liveworking=LIVE','http://sailingschedules2.maerskline.com/MaerskSailingSchedulesCustomerWeb/CustomerWebServlet?ssaction=com.saf.ss.cust.action.route.ShowRoute&fromRegionID=2&toRegionID=3&liveworking=LIVE']
    
    service_urls = []
    for url in urls:
        response = urllib2.urlopen(url)
        html = response.read()
        #region_logger.debug("html from middle page: {0}".format(html))
        soup = BeautifulSoup(html)
        # get the table with all the links to service routes
        table = soup.find('table', 'tblData')
        #region_logger.debug("table from middle page: {0}".format(table))
        links = table.findAll('a')
        for link in links:
            if 'html' in link['href']:
                service_urls.append(link['href'])
    return service_urls



# Entry point
    
parser = OptionParser()
parser.add_option("-c", "--config", dest="config",
                  help="pull configuration from this file, example --config /path/to/config.ini", metavar="CONFIGFILE")
(options, args) = parser.parse_args()

if options.config is not None:
    config.read(options.config)
    start()
    #get_schedule_urls()
else:  
    print "Sorry You must specify a configuration file, python -m maersk.parser -c <config_file>"  
    sys.exit(1)
