import random
import unittest
from pageparser import PageParser
from datetime import datetime as dt
from bs4 import BeautifulSoup
import pprint

class DateCellParseTest(unittest.TestCase):

    def setUp(self):
        self.parser = PageParser("http://www.shipmentlink.com/tvs2/download_txt/NUE_W.html")
        
    def test_date_with_transfer(self):
        html = """<td colspan='1' class='f09rown2' nowrap>06/23(Transfer to TAE service<BR> <a href='#' onClick="window.open('http://www.shipmentlink.com/tvs2/jsp/TVS2_ShowVesselSchedule.jsp?vessel_name=Ital Libera&vessel_code=LIBE&vessel_voyage=0248-059E','win1','left=250,top=150,width=450,height=500,toolbar=0,menubar=0,resizable=0,scrollbars=1,status=0');">Ital Libera 0248-059E</a>)</td>"""
        print self.parser.parse_date(BeautifulSoup(html))
        
    def test_date_with_two_dates(self):
        html = """<td class='f09rown1' nowrap>06/11<BR>06/12</td>"""
        print self.parser.parse_date(BeautifulSoup(html))
                
    def test_ports_row(self):
        portshtml = '''<tr><td colspan="2" class="f09tilb1"> &nbsp;  </td><td class="f09tilb1">CHARLESTON</td><td class="f09tilb1">BALTIMORE</td><td class="f09tilb1">NORFOLK</td><td class="f09tilb1">NEW YORK</td><td class="f09tilb1">COLON CONTAINER TERMINAL</td><td class="f09tilb1">PANAMA CANAL</td><td class="f09tilb1">LOS ANGELES</td><td class="f09tilb1">OAKLAND</td><td class="f09tilb1">TOKYO</td><td class="f09tilb1">PUSAN</td><td class="f09tilb1">YANTIAN</td><td class="f09tilb1">HONG KONG</td><td class="f09tilb1">KAOHSIUNG</td><td class="f09tilb1">QINGDAO</td><td class="f09tilb1">SHANGHAI</td><td class="f09tilb1">NINGBO</td><td class="f09tilb1">LAEM CHABANG</td><td class="f09tilb1">XINGANG</td><td class="f09tilb1">SHANGHAI</td></tr>'''        
        print self.parser.parse_ports_row(BeautifulSoup(portshtml))
        
    def test_parse_voyage_row(self):
        voyagehtml = """<tr><td nowrap="" class="f09rown2">EVER RACER 0636-113W</td><td nowrap="" class="f09rown2">ARR<br>DEP</td><td nowrap="" class="f09rown2">05/18<br>05/18</td><td nowrap="" class="f09rown2">---<br>---</td><td nowrap="" class="f09rown2">05/19<br>05/20</td><td nowrap="" class="f09rown2">05/21<br>05/22</td><td nowrap="" class="f09rown2">05/26<br>05/27</td><td nowrap="" class="f09rown2">05/28<br>05/28</td><td nowrap="" class="f09rown2">06/06<br>06/07</td><td nowrap="" class="f09rown2">06/08<br>06/08</td><td nowrap="" class="f09rown2">06/22<br>06/23</td><td nowrap="" class="f09rown2">06/25<br>06/26</td><td nowrap="" class="f09rown2">---<br>---</td><td nowrap="" class="f09rown2">---<br>---</td><td nowrap="" class="f09rown2">---<br>---</td><td nowrap="" class="f09rown2">06/27<br>06/28</td><td nowrap="" class="f09rown2">06/29<br>06/30</td><td nowrap="" class="f09rown2">06/30<br>07/01</td><td nowrap="" class="f09rown2" colspan="3">07/11(Transfer to AGI service<br> <a onclick="window.open('http://www.shipmentlink.com/tvs2/jsp/TVS2_ShowVesselSchedule.jsp?vessel_name=Ever Racer&amp;vessel_code=RACR&amp;vessel_voyage=041W','win1','left=250,top=150,width=450,height=500,toolbar=0,menubar=0,resizable=0,scrollbars=1,status=0');" href="#">Ever Racer 041W</a>)</td></tr>"""
        portshtml = '''<tr><td colspan="2" class="f09tilb1"> &nbsp;  </td><td class="f09tilb1">CHARLESTON</td><td class="f09tilb1">BALTIMORE</td><td class="f09tilb1">NORFOLK</td><td class="f09tilb1">NEW YORK</td><td class="f09tilb1">COLON CONTAINER TERMINAL</td><td class="f09tilb1">PANAMA CANAL</td><td class="f09tilb1">LOS ANGELES</td><td class="f09tilb1">OAKLAND</td><td class="f09tilb1">TOKYO</td><td class="f09tilb1">PUSAN</td><td class="f09tilb1">YANTIAN</td><td class="f09tilb1">HONG KONG</td><td class="f09tilb1">KAOHSIUNG</td><td class="f09tilb1">QINGDAO</td><td class="f09tilb1">SHANGHAI</td><td class="f09tilb1">NINGBO</td><td class="f09tilb1">LAEM CHABANG</td><td class="f09tilb1">XINGANG</td><td class="f09tilb1">SHANGHAI</td></tr>'''
        self.parser.parse_ports_row(BeautifulSoup(portshtml))
        voyagedata = self.parser.parse_voyage_row(BeautifulSoup(voyagehtml))
        # assert that the following fields exists in the data
        self.assertIn('vessel',voyagedata)
        self.assertEqual('EVER RACER', voyagedata['vessel'])
        self.assertIn('voyage', voyagedata)
        self.assertEqual('0636-113W', voyagedata['voyage'])
        self.assertIn('scrape_date' ,voyagedata)
        self.assertIn('url', voyagedata)
        self.assertIn('ports', voyagedata)
        
        for port in voyagedata['ports']:
            if port['port'] == "CHARLESTON":
                self.assertEqual(port['eta'].strftime("%m/%d"), "05/18")
                self.assertEqual(port['etd'].strftime("%m/%d"), "05/18")
            elif port['port'] == "NORFOLK":
                self.assertEqual(port['eta'].strftime("%m/%d"), "05/19")
                self.assertEqual(port['etd'].strftime("%m/%d"), "05/20")
            elif port['port'] == "NEW YORK":
                self.assertEqual(port['eta'].strftime("%m/%d"), "05/21")
                self.assertEqual(port['etd'].strftime("%m/%d"), "05/22")
            elif port['port'] == "COLON CONTAINER TERMINAL":
                self.assertEqual(port['eta'].strftime("%m/%d"), "05/26")
                self.assertEqual(port['etd'].strftime("%m/%d"), "05/27")
            elif port['port'] == "PANAMA CANAL":
                self.assertEqual(port['eta'].strftime("%m/%d"), "05/28")
                self.assertEqual(port['etd'].strftime("%m/%d"), "05/28")
            elif port['port'] == "LOS ANGELES":
                self.assertEqual(port['eta'].strftime("%m/%d"), "06/06")
                self.assertEqual(port['etd'].strftime("%m/%d"), "06/07")
            elif port['port'] == "OAKLAND":
                self.assertEqual(port['eta'].strftime("%m/%d"), "06/08")
                self.assertEqual(port['etd'].strftime("%m/%d"), "06/08")
            elif port['port'] == "TOKYO":
                self.assertEqual(port['eta'].strftime("%m/%d"), "06/22")
                self.assertEqual(port['etd'].strftime("%m/%d"), "06/23")
            elif port['port'] == "PUSAN":
                self.assertEqual(port['eta'].strftime("%m/%d"), "06/25")
                self.assertEqual(port['etd'].strftime("%m/%d"), "06/26")
            elif port['port'] == "QINGDAO":
                self.assertEqual(port['eta'].strftime("%m/%d"), "06/27")
                self.assertEqual(port['etd'].strftime("%m/%d"), "06/28")
            elif port['port'] == "SHANGHAI":
                self.assertEqual(port['eta'].strftime("%m/%d"), "06/29")
                self.assertEqual(port['etd'].strftime("%m/%d"), "06/30")
            elif port['port'] == "NINGBO":
                self.assertEqual(port['eta'].strftime("%m/%d"), "06/30")
                self.assertEqual(port['etd'].strftime("%m/%d"), "07/01")
            elif port['port'] == "LAEM CHABANG":
                self.assertEqual(port['eta'].strftime("%m/%d"), "07/11")
                self.assertEqual(port['etd'].strftime("%m/%d"), "07/11")

        
        
    
    def test_parser(self):
        results = self.parser.parse()
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(results)
        for result in results:
            if result['vessel'] == "EVER RACER" and result['voyage'] == "0636-113W":
                self.assertIn('vessel',result)
                self.assertEqual('EVER RACER', result['vessel'])
                self.assertIn('voyage', result)
                self.assertEqual('0636-113W', result['voyage'])
                self.assertIn('scrape_date' ,result)
                self.assertIn('url', result)
                self.assertIn('ports', result)
                ports = result['ports']
                for port in ports:
                    if port['port'] == "CHARLESTON":
                        self.assertEqual(port['eta'].strftime("%m/%d"), "05/18")
                        self.assertEqual(port['etd'].strftime("%m/%d"), "05/18")
                    elif port['port'] == "NORFOLK":
                        self.assertEqual(port['eta'].strftime("%m/%d"), "05/19")
                        self.assertEqual(port['etd'].strftime("%m/%d"), "05/20")
                    elif port['port'] == "NEW YORK":
                        self.assertEqual(port['eta'].strftime("%m/%d"), "05/21")
                        self.assertEqual(port['etd'].strftime("%m/%d"), "05/22")
                    elif port['port'] == "COLON CONTAINER TERMINAL":
                        self.assertEqual(port['eta'].strftime("%m/%d"), "05/26")
                        self.assertEqual(port['etd'].strftime("%m/%d"), "05/27")
                    elif port['port'] == "PANAMA CANAL":
                        self.assertEqual(port['eta'].strftime("%m/%d"), "05/28")
                        self.assertEqual(port['etd'].strftime("%m/%d"), "05/28")
                    elif port['port'] == "LOS ANGELES":
                        self.assertEqual(port['eta'].strftime("%m/%d"), "06/06")
                        self.assertEqual(port['etd'].strftime("%m/%d"), "06/07")
                    elif port['port'] == "OAKLAND":
                        self.assertEqual(port['eta'].strftime("%m/%d"), "06/08")
                        self.assertEqual(port['etd'].strftime("%m/%d"), "06/08")
                    elif port['port'] == "TOKYO":
                        self.assertEqual(port['eta'].strftime("%m/%d"), "06/22")
                        self.assertEqual(port['etd'].strftime("%m/%d"), "06/23")
                    elif port['port'] == "PUSAN":
                        self.assertEqual(port['eta'].strftime("%m/%d"), "06/25")
                        self.assertEqual(port['etd'].strftime("%m/%d"), "06/26")
                    elif port['port'] == "QINGDAO":
                        self.assertEqual(port['eta'].strftime("%m/%d"), "06/27")
                        self.assertEqual(port['etd'].strftime("%m/%d"), "06/28")
                    elif port['port'] == "SHANGHAI":
                        self.assertEqual(port['eta'].strftime("%m/%d"), "06/29")
                        self.assertEqual(port['etd'].strftime("%m/%d"), "06/30")
                    elif port['port'] == "NINGBO":
                        self.assertEqual(port['eta'].strftime("%m/%d"), "06/30")
                        self.assertEqual(port['etd'].strftime("%m/%d"), "07/01")
                    elif port['port'] == "LAEM CHABANG":
                        self.assertEqual(port['eta'].strftime("%m/%d"), "07/11")
                        self.assertEqual(port['etd'].strftime("%m/%d"), "07/11")
    
    
if __name__ == '__main__':
    unittest.main()