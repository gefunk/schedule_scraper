from optparse import OptionParser
import sys, ConfigParser
import MySQLdb
from pymongo import MongoClient
from bson.objectid import ObjectId


# initialize config parser
config = ConfigParser.RawConfigParser()


'''
Connects ports scraped from sites to ports in the database
This connection will allow us to show additional information for ports (lat, long, etc..)

The ports database is in mysql, it is derived from the UN database
'''
def rationalize():
    # mysql
    host = config.get("mysql", "host")
    user = config.get("mysql", "user")
    passwd = config.get("mysql", "password")
    db = config.get("mysql", "db")
    mconnection = MySQLdb.connect(host=host,user=user, passwd=passwd, db=db)
    cursor = mconnection.cursor()
    
    # mongo connection
    uri = config.get("mongodb", "uri")
    connection = MongoClient(uri)
    db = connection[config.get("mongodb", "db")]

    find_in_ports_rational_table = "select ref_ports_id, mongoid, mongoname from rationalize_schedules where mongoid='{0}'"
    insert_in_ports_rational_table = '''insert into rationalize_schedules (mongoid, ref_ports_id, mongoname) values (%(mongoid)s, %(refportid)s, %(mongoname)s)'''

    find_ports_sql = '''select * from ref_ports where name like '%{0}%' and ocean=1 order by hit_count desc, found desc, population desc limit 1'''
    find_ports_by_id_sql = '''select * from ref_ports where id={0}'''

    # initialize collection
    ports_collection = db.ports
    
    
    # find ports which have not been found in mysql
    not_found_ports = ports_collection.find({"info" : {"$exists": False}})
    # attempt to rationalize ports
    for port in not_found_ports:
        cursor.execute(find_in_ports_rational_table.format(port["_id"]))
        rationalport = cursor.fetchone()
        # find port either by id or by name
        if rationalport:
            port_id = rationalport[0]
            cursor.execute(find_ports_by_id_sql.format(port_id))
        else:
            cursor.execute(find_ports_sql.format(MySQLdb.escape_string(port['name'])))
        
        num_fields = len(cursor.description)
        field_names = [i[0] for i in cursor.description]
        for row in cursor.fetchall():
            # convert mysql row to mongodb object
            mport = {}
            for index, value in enumerate(row):
                mport[field_names[index]] = value 
            # save into mongodb
            port['info'] = mport
            ports_collection.save(port)
        
        if not rationalport:
            data = {"mongoid":port["_id"], "refportid":0, "mongoname":port['name']}
            if 'info' in port:
                data['refportid'] = port['info']['id']
            cursor.execute(insert_in_ports_rational_table, data)
            mconnection.commit()
    
    # close connections after completed
    mconnection.close()
    connection.close()
            
'''
Update ports in the schedules collection
Adds port information to every port in the schedule collection
this will allow the web app to show lat, long, etc... information
along with the schedules
'''
def update_ports():
    # mongo connection
    uri = config.get("mongodb", "uri")
    connection = MongoClient(uri)
    db = connection[config.get("mongodb", "db")]
    
    # initialize collection
    ports_collection = db.ports
    schedule_collection = db.schedules_temp
    
    for voyage in schedule_collection.find():
        for port in voyage['ports']:
            if not 'info' in port:
                port_info = ports_collection.find_one({"name":port['port']}, {"info": 1})
                if 'info' in port_info:
                    port_data = port_info['info'] 
                    port['port_info'] = {
                        "latitude": port_data["latitude"], 
                        "longitude": port_data["longitude"],
                        "port_code": port_data["port_code_c"],
                        "city_code": port_data['port_code'],
                        "country_code": port_data['country_code']
                    }
        schedule_collection.save(voyage);
    
    

'''
Copy over ports from schedules collection to ports collection
only copies ports that do not already exist
'''
def copy_distinct_ports_from_schedules():
    # mongo connection
    uri = config.get("mongodb", "uri")
    connection = MongoClient(uri)
    db = connection[config.get("mongodb", "db")]
    
    schedule_collection = db.schedules_temp
    ports_collection = db.ports
    
    ports = schedule_collection.distinct("ports.port")
    
    # copy over ports that don't exist in the ports collection
    for port in ports:
        if ports_collection.find_one({"name":port}) is None:
            ports_collection.save({"name":port})
    

'''
One time copy of distinct ports to rationalize schedules table
this should only be used once to populate the table
'''
def one_time_copy_distinct_ports_to_mysql_rationalize_schedules():
    # mysql
    host = config.get("mysql", "host")
    user = config.get("mysql", "user")
    passwd = config.get("mysql", "password")
    db = config.get("mysql", "db")
    mconnection = MySQLdb.connect(host=host,user=user, passwd=passwd, db=db)
    cursor = mconnection.cursor()
    
    # mongo connection
    uri = config.get("mongodb", "uri")
    connection = MongoClient(uri)
    db = connection[config.get("mongodb", "db")]
    
    insert_in_ports_rational_table = '''insert into rationalize_schedules (mongoid, ref_ports_id, mongoname) values (%(mongoid)s, %(refportid)s, %(mongoname)s)'''
    
    ports_collection = db.ports
    
    for port in ports_collection.find({},{"info.id":1, "name":1}):
        data = {"mongoid": port['_id'], "refportid": 0, "mongoname": port['name'] }
        if 'info' in port:
            data['refportid'] = port['info']['id']
        cursor.execute(insert_in_ports_rational_table, data)
        mconnection.commit()
    




parser = OptionParser()
parser.add_option("-c", "--config", dest="config",
                  help="pull configuration from this file, example --config /path/to/config.ini", metavar="CONFIGFILE")
parser.add_option("-a", "--action", dest="action",
                  help="what action to accomplish, e.g.: copy, rationalize")                  
(options, args) = parser.parse_args()

if options.config is not None:
    config.read(options.config)
else:  
    print "Sorry You must specify a configuration file: -c <config_file>"  
    sys.exit(1)
    
if options.action is not None:
    if options.action == 'copy':
        copy_distinct_ports_from_schedules()
    elif options.action == 'rationalize':
        rationalize()
    elif options.action == 'update':
        update_ports()
    elif options.action == 'once':
        one_time_copy_distinct_ports_to_mysql_rationalize_schedules()
    
else:  
    print "Sorry You must specify an action: -a <copy/rationalize>"  
    sys.exit(1)

