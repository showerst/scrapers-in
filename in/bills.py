import lxml.html
from pupa.scrape import Scraper, Bill, VoteEvent
from lxml import etree

class IndiaBillScraper(Scraper):
    base_url = 'http://164.100.47.194/'
    search_url = 'http://164.100.47.194/Loksabha/Legislation/NewAdvsearch.aspx'


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

        # GET the doc once to set up our viewstate variables
        doc = lxml.html.fromstring(self.get(url=self.search_url).content)
        (viewstate, ) = doc.xpath('//input[@id="__VIEWSTATE"]/@value')
        (viewstategenerator, ) = doc.xpath(
            '//input[@id="__VIEWSTATEGENERATOR"]/@value')
        (eventvalidation, ) = doc.xpath('//input[@id="__EVENTVALIDATION"]/@value')

        form = {
            'ctl00$ContentPlaceHolder1$RadioBttnhouse':'ls',
            'ctl00$ContentPlaceHolder1$RadioBttnbilltyp':'All',
            # Bill Status: All
            'ctl00$ContentPlaceHolder1$RadioButtonList1':'6',
            'ctl00$ContentPlaceHolder1$ddlYear1':'2017',
            'ctl00$ContentPlaceHolder1$ddlYear2':'2017',
            'ctl00$ContentPlaceHolder1$ddlMember': '--- Please Select ---',
            'ctl00$ContentPlaceHolder1$RadioBttnmember':'current',
            'ctl00$ContentPlaceHolder1$ddlMinistry':'--- Please Select ---',
            'ctl00$ContentPlaceHolder1$ddlCategory':'--- Please Select ---',
            'ctl00$ContentPlaceHolder1$btnsbmt':'Submit',
            'ctl00$ContentPlaceHolder1$ddlfile':'.pdf',
            'ctl00$ContentPlaceHolder1$STitle':'',
            '__VIEWSTATE':viewstate,
            '__VIEWSTATEGENERATOR':viewstategenerator,
            '__EVENTVALIDATION':eventvalidation,
            '__VIEWSTATEENCRYPTED':'',
            '__EVENTTARGET':'',
            '__EVENTARGUMENT':'',
            '__LASTFOCUS':'',
            'ctl00$txtSearchGlobal':''
        }

        # Then post to submit the form
        page = self.submit_search(form)

        yield self.scrape_table(page)

        pagination = page.xpath('//table//tr[contains(@class,"page-nav")]//table//tr/td/font/a/font/text()')

        for td in pagination:
            print("Submitting {}", td)
            form['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder1$GR1'
            form['__EVENTARGUMENT'] = 'Page${}'.format(td)
            page = self.submit_search(form)

            yield self.scrape_table(page)
    
    def latest_session(self):
        return '2017'

    def scrape_table(self, page):
        for tr in page.xpath('//table[@id="ContentPlaceHolder1_GR1"]/tr')[2:]:
            print( lxml.etree.tostring(tr))
            year = tr.xpath('td[1]/text()')[0]
            bill_no = tr.xpath('td[2]/text()')[0]
            title = tr.xpath('td[3]/a[1]/text()')[0].strip()
            versions = tr.xpath('td[3]/a')[1:]
            bill = Bill(identifier=bill_no,
                legislative_session=year,
                title=title,
                classification="resolution")
            
            bill.add_source(self.base_url)
            #print( tr.xpath('td[3]/a[3]/text()'))
            yield bill

    def submit_search(self, form):
        # Post to submit the form
        resp = self.post(url=self.search_url, data=form, allow_redirects=True)
        page = lxml.html.fromstring(resp.content)
        page.make_links_absolute(self.base_url)
        return page
