import lxml.html
from pupa.scrape import Scraper, Bill, VoteEvent
from lxml import etree

class IndiaBillScraper(Scraper):
    def scrape(self,session=None,chamber=None):
        if not session:
            session = self.latest_session()
            self.info('no session specified, using %s', session)
        
        chambers = [chamber] if chamber else ['upper', 'lower']
        for chamber in chambers:
            yield from self.scrape_chamber(session, chamber)
    
    def scrape_chamber(self,session,chamber):
        base_url = 'http://164.100.47.194/Loksabha/Legislation/'
        url = 'http://164.100.47.194/Loksabha/Legislation/NewAdvsearch.aspx'
        form = {
            'ctl00$ContentPlaceHolder1$RadioBttnhouse':'ls',
            'ctl00$ContentPlaceHolder1$RadioBttnbilltyp':'All',
            # Bill Status: All
            'ctl00$ContentPlaceHolder1$RadioButtonList1':'6',
            'ctl00$ContentPlaceHolder1$ddlYear1':'2017',
            'ctl00$ContentPlaceHolder1$ddlYear2':'2017'
        }
        resp = self.post(url=url, data=form, allow_redirects=True)
        page = lxml.html.fromstring(resp.content)
        page.make_links_absolute(base_url)

        for tr in page.xpath('//table[@id="ContentPlaceHolder1_GR1"]/tr')[1:]:
            print( lxml.etree.tostring(tr))
            print( tr.xpath('td[1]/text()'))
            print( tr.xpath('td[2]/text()'))
            print( tr.xpath('td[3]/a[1]/text()'))
            print( tr.xpath('td[3]/a[2]/text()'))
            print( tr.xpath('td[3]/a[3]/text()'))
        pass
    
    def latest_session(self):
        return '2017'
