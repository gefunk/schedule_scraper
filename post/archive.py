
from optparse import OptionParser
import sys, ConfigParser, time, datetime
from pymongo import MongoClient
from bson.objectid import ObjectId



# initialize config parser
config = ConfigParser.RawConfigParser()
# archive the data into csv file
def start():
    uri = config.get("mongodb", "uri")
    connection = MongoClient(uri)
    db = connection[config.get("mongodb", "db")]
    schedule_collection = db.schedules
    
    file_path = config.get('archive', 'path')
    timestr = time.strftime("%Y_%m_%d")
    f = open(file_path+timestr+"_scraper.csv", 'w')

    for voyage in schedule_collection.find():
        for port in voyage['ports']:
            scrape_date = schedule["scrape_date"].strftime("%Y-%m-%d %H:%M:%S")
            carrier = schedule["carrier"]
            vessel = schedule["vessel"]
            voyage_number = voyage['voyage']
            print port
            port_name = port['port']
            eta = port['eta'].strftime("%Y-%m-%d %H:%M:%S")
            etd = port['etd'].strftime("%Y-%m-%d %H:%M:%S")
            print scrape_date
            
            f.write(carrier+"|"+vessel+"|"+scrape_date+"|"+voyage_number+"|"+port_name+"|"+eta+"|"+etd+"\n")
    
    # close file
    f.close()
    connection.close()
                

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
