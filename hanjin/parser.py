
from routeparser import RouteParser
from optparse import OptionParser
import sys, ConfigParser
from datetime import datetime as dt
from pymongo import MongoClient
from bson.objectid import ObjectId
import pprint

# initialize config parser
config = ConfigParser.RawConfigParser()

continents = ['AA', 'MN', 'ML', 'EE', 'FF']
    
def start():
    
    routeParser = RouteParser("http://www.hanjin.com/hanjin/CUP_HOM_3007GS.do")
    
    # mongo connection
    uri = config.get("mongodb", "uri")
    connection = MongoClient(uri)
    db = connection[config.get("mongodb", "db")]
    
    from_continents = continents
    to_continents = continents
    
    log = {"start": dt.now(), "carrier":"Hanjin"}
    
    # cross product of from continents and to continents gives us all the routes
    for fc in from_continents:
        for tc in to_continents:
            routes = routeParser.get_routes_by_continent(fc, tc)
            for route in routes:
                ports = routeParser.get_port_heading(route['code'])
                data = routeParser.get_route(route['name'], route['code'], ports)
                for voyage in data:
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