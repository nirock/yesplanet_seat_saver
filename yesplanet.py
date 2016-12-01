import requests
import re
import time
import random

def get_input_value_by_id(input_id, data):
    return re.findall('id="%s" value="(.*)"' % (input_id), data)[0]
    
class YesplanetSeatSaver(object):
    def __init__(self, tickets_url):
        # tickets_url = https://www.yesplanet.co.il/ecom?s=1010003&p=107219112916-191680#ready
        self._tickets_url = tickets_url
        self._ec = re.findall(r".*=(\d+-\d+).*", tickets_url)[0]
        self._dtticks = None

        self._step0_text = None
        self._rbzid = None
        self._step1_text = None
        self._step2_text = None
        self._step3_text = None
        self._step4_text = None
        self._step5_text = None

        self._session = requests.Session()

    def step0(self):
        step0 = self._session.get(r"https://tickets.yesplanet.co.il/ypr/NewSessionRedirector.aspx?key=1072&redirect=%s" % (self._tickets_url))
        
        self._step0_text = step0.text
    
    def get_rbzid_page(self):
        assert self._step0_text is not None
        rbzid_page = self._step0_text.replace(r'setTimeout(function(){var U="reload",b="location";window[b][U]();},1)', "")
        rbzid_page = rbzid_page.replace(r"T=window[g][j];", r"T=window[g][j];document.write(D);")
        return rbzid_page

    def step0_5(self, rbzid):
        ''' Setting rbzid '''
        self._rbzid = rbzid
        self._session.cookies.set("rbzid", rbzid)
    
    def step1(self):
        #https://tickets.yesplanet.co.il/ypr/?key=1072&ec=107211113016-191815
        assert self._rbzid is not None, "You didn't run step0_5"
        step1 = self._session.get(r"https://tickets.yesplanet.co.il/ypr/?key=1072&ec=%s" % (self._ec))
        self._step1_text = step1.text.encode('utf-8')
        self._dtticks = re.findall(r'dtticks=(\d+)&amp;', self._step1_text)[0]

    def step2(self):
        assert self._dtticks is not None, "You didn't run step1"
        step2 = self._session.get("https://tickets.yesplanet.co.il/ypr/SelectTicketsPage.aspx?dtticks=%s&hideBackButton=1" % (self._dtticks))
        self._step2_text = step2.text.encode("utf-8")
    
    def step3(self, number_of_tickets):
        assert self._dtticks is not None, "You didn't run step1"
        assert self._step2_text is not None, "You didn't run step2"
        data = {
            "__EVENTTARGET": "ctl00$CPH1$lbNext1",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": get_input_value_by_id("__VIEWSTATE", self._step2_text),
            "__VIEWSTATEGENERATOR": get_input_value_by_id("__VIEWSTATEGENERATOR", self._step2_text),
            "__EVENTVALIDATION": get_input_value_by_id("__EVENTVALIDATION", self._step2_text),
            "hfSKey": get_input_value_by_id("hfSKey", self._step2_text),
            "hfOIKey": get_input_value_by_id("hfOIKey", self._step2_text),
            "ctl00$CPH1$SelectTicketControl1$rptTicketSelectionGrid$ctl00$TicketsSelection$ctl02$ddQunatity":number_of_tickets,
            "ctl00$CPH1$SelectTicketControl1$rptTicketSelectionGrid$ctl00$TicketsSelection$ctl03$ddQunatity":0,
            "ctl00$CPH1$SelectTicketControl1$TicketGroupId":"",
            "ctl00$CPH1$SelectTicketControl1$hdnSelectedTicketGroupIdInTicketMode":0,
        }
        step3 = self._session.post("https://tickets.yesplanet.co.il/ypr/SelectTicketsPage.aspx?dtticks=%s&hideBackButton=1" % (self._dtticks), data=data)
    
    def step4(self):
        assert self._dtticks is not None, "You didn't run step1"
        step4 = self._session.get(r"https://tickets.yesplanet.co.il/ypr/SelectSeatPage2.aspx?dtticks=%s" % (self._dtticks))
        self._step4_text = step4.text.encode("utf-8")
    
    def get_seat_selector_page(self):
        assert self._step4_text is not None, "You didn't run step4"
        sps = self._step4_text.replace("<title>", r'<base href="%s" target="_blank"><title>' % ("https://tickets.yesplanet.co.il/ypr/"))
        sps = sps.replace(r'id="tbSelectedSeats" type="hidden"', r'id="tbSelectedSeats" type="text" style="position:absolute;left:0;top:0;"')
        return sps
    
    def step5(self, seat_selection):
        assert self._dtticks is not None, "You didn't run step1"
        assert self._step2_text is not None, "You didn't run step2"
        assert self._step4_text is not None, "You didn't run step4"
        data = {
            "__EVENTTARGET": "ctl00$CPH1$SPC$lnkSubmit",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": get_input_value_by_id("__VIEWSTATE", self._step4_text),
            "__VIEWSTATEGENERATOR": get_input_value_by_id("__VIEWSTATEGENERATOR", self._step4_text),
            "__EVENTVALIDATION": get_input_value_by_id("__EVENTVALIDATION", self._step4_text),
            "hfSKey": get_input_value_by_id("hfSKey", self._step2_text),
            "hfOIKey": get_input_value_by_id("hfOIKey", self._step2_text),
            "ctl00$CPH1$SPC$hfVenueAndSectionId": get_input_value_by_id("ctl00_CPH1_SPC_hfVenueAndSectionId", self._step4_text),
            "tbSelectedSeats": seat_selection
        }
        
        step5 = self._session.post(r"https://tickets.yesplanet.co.il/ypr/SelectSeatPage2.aspx?dtticks=%s" % (self._dtticks), data=data)
        self._step5_text = step5.text.encode('utf-8')
        if "ctl00_CPH1_OrderFormControl1_SessionInfoTimerControl1_lblSeatLockInfo".encode("utf-8") not in self._step5_text: 
            return False
        return True
    
    @staticmethod
    def run_from_raw_input():
        def show_page(page_data):
            with open(r"page.html", "wb") as f: f.write(page_data)
            import webbrowser
            webbrowser.open(r"page.html")

        tickets_url = raw_input("Please enter tickets url: ")
        with YesplanetSeatSaver(tickets_url) as yss:
            yss.step0()
            show_page(yss.get_rbzid_page())
            rbzid = raw_input("Please enter rbzid (the output from pop-uped page): ")
            yss.step0_5(rbzid)
            yss.step1()
            yss.step2()
            number_of_tickets = raw_input(r"Please enter number of tickets: ")
            yss.step3(number_of_tickets)
            yss.step4()
            show_page(yss.get_seat_selector_page())
            seat_selection = raw_input(r"Please enter your seat selection: ")
            while True:
                if (yss.step5(seat_selection) is True):
                    print "Saved seats successfuly"
                sleeping_time = 60 + random.randint(10,50)
                print "Sleeping for a %d seconds" % (sleeping_time)
                time.sleep(sleeping_time)

    def free_tickets(self):
        if self._step4_text is not None:
            self.step5(1)
            self.step5(2)

    def close(self):
        self.free_tickets()
        self._session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == "__main__":
    YesplanetSeatSaver.run_from_raw_input()
    