import urllib2
from pageparser import PageParser
from optparse import OptionParser
import sys, ConfigParser
from datetime import datetime as dt
from pymongo import MongoClient
from bson.objectid import ObjectId
from bs4 import BeautifulSoup, SoupStrainer
import pprint



# initialize config parser
config = ConfigParser.RawConfigParser()



'''
get all schedule URLS
@return all urls that need to be scraped
'''
def get_all_schedule_urls():
    response = urllib2.urlopen('http://www.shipmentlink.com/tvs2/jsp/TVS2_LongTermMenu.jsp?type=L')
    links = []
    # retrieve all links from page
    for link in BeautifulSoup(response, parse_only=SoupStrainer('a')):
        # get all links which have download_txt and end in html
        if link.has_attr('href') and "download_txt" in link['href'] and "html" in link['href']:
            link_split = link['href'].split("'")
            # add the raw link, and strip the leading ..
            links.append("http://www.shipmentlink.com/tvs2"+(link_split[1].strip("..")))
    
    return links


def start():
    
    # mongo connection
    uri = config.get("mongodb", "uri")
    connection = MongoClient(uri)
    db = connection[config.get("mongodb", "db")]
    
    
    for link in get_all_schedule_urls():
        log = {"start": dt.now(), "url": link, "carrier": "Evergreen"}
        parser = PageParser(link)
        schedules = parser.parse()
        
        for voyage in schedules:
            voyage['carrier'] = "Evergreen"
            db.schedules_temp.save(voyage)
        
        log['finish'] = dt.now()
        db.scrapelogs.insert(log)
        
    


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
