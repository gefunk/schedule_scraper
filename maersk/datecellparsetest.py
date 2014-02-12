import random
import unittest
from pageparser import PageParser
from datetime import datetime as dt	


class DateCellParseTest(unittest.TestCase):

    def setUp(self):
        self.parser = PageParser("http://www.google.com")
        
        
    def test_cell_parse_one_date_arrived(self):
        one_arrived = '''<td nowrap="" align="center" class="schedulecell">
			  			    <span class="schedulearrived">06</span>
			  			  -
			  			    08 Feb
			  			</td>'''
        self.assertEqual("06-08Feb", self.parser.parse_date_cell(one_arrived))  
        eta = dt.strptime("06/Feb/"+str(dt.now().year),"%d/%b/%Y")
        etd = dt.strptime("08/Feb/"+str(dt.now().year),"%d/%b/%Y")
        self.assertEqual(eta, self.parser.parse_dates("06-08Feb")[0])
        self.assertEqual(etd, self.parser.parse_dates("06-08Feb")[1])
    
    def test_cell_both_months(self):
        both_months = '''<td nowrap="" align="center" class="schedulecell">
						    30 Jun
					  	-
		  				    01 Jul
					      </td>'''
        self.assertEqual("30Jun-01Jul", self.parser.parse_date_cell(both_months))    
        eta = dt.strptime("30/Jun/"+str(dt.now().year),"%d/%b/%Y")
        etd = dt.strptime("01/Jul/"+str(dt.now().year),"%d/%b/%Y")
        self.assertEqual(eta, self.parser.parse_dates("30Jun-01Jul")[0])
        self.assertEqual(etd, self.parser.parse_dates("30Jun-01Jul")[1])
        
        
    
    
if __name__ == '__main__':
    unittest.main()