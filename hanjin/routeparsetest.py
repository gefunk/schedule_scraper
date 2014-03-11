import random
import unittest
from routeparser import RouteParser
from datetime import datetime as dt	
import pprint

class RouteParseTest(unittest.TestCase):

    def setUp(self):
        self.parser = RouteParser("http://www.hanjin.com/hanjin/CUP_HOM_3007GS.do")
        
        ''' def test_port_heading(self):
        results = self.parser.get_port_heading('AWC')
        self.assertIsNotNone(results)
        self.assertEqual(10, len(results))
        self.assertIn("QINGDAO,CHINA", results)
        self.assertIn("SHANGHAI", results)
        self.assertIn("NINGBO,ZHEJIANG", results)
        self.assertIn("YOKOHAMA", results)
        self.assertIn("PANAMA CANAL", results)
        self.assertIn("NEW YORK,NY", results)
        self.assertIn("BOSTON,MA", results)
        self.assertIn("NORFOLK,VA", results)'''
        
    
    def test_get_routes_by_continent(self):
        routes = self.parser.get_routes_by_continent("AA", "AA")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(routes)
    
    def test_get_two_digit_num_code(self):
        self.assertEqual(10, self.parser.get_two_digit_num_code("dep10"))
        self.assertEqual(1, self.parser.get_two_digit_num_code("dep01"))
        self.assertEqual(1, self.parser.get_two_digit_num_code("arr01"))
        self.assertNotEqual(123, self.parser.get_two_digit_num_code("dep123"))
        self.assertEqual(10, self.parser.get_two_digit_num_code("arr10"))
        
    def test_get_route(self):
        ports = self.parser.get_port_heading('TSS')
        schedules = self.parser.get_route('some route service','TSS', ports)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(schedules)
        
if __name__ == '__main__':
    unittest.main()