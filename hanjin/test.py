import urllib
import urllib2
import json
from datetime import datetime

url = 'http://www.hanjin.com/hanjin/CUP_HOM_3007GS.do'
values = {'f_cmd' : '121',
          'frm_conti_cd' : 'AA',
          'to_conti_cd': 'AA'}
values = {"f_cmd":'123',
            "rows":'10000',
            "_search":'false',
            "sord":'asc',
            "vsl_slan_cd":'LW1',
            "page":'1'}

data = urllib.urlencode(values)
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
the_page = response.read()

obj = json.loads(the_page)

print obj

