# coding: utf-8
#from opencivicdata.divisions import Division
from pupa.scrape import Organization
from pupa.scrape import Jurisdiction

from datetime import datetime

from .people import IndiaPersonScraper

class India(Jurisdiction):
    classification = 'legislature'
    division_id = 'ocd-division/country:in'
    division_name = 'India'
    name = 'Parliament of India'
    url = 'http://parliamentofindia.nic.in/'
    parties = [
        {'name': 'National Democratic Alliance'},
        {'name': 'United Progressive Alliance'},
        {'name': 'Bharatiya Janata Party'},
    ]
    scrapers = {
        "people": IndiaPersonScraper,
    }    

    def get_organizations(self):
        parliament = Organization(self.name, classification=self.classification)
        yield parliament

        upper = Organization('Rajya Sabha', classification='upper', parent_id=parliament)
        lower = Organization('Lok Sabha', classification='lower', parent_id=parliament)

        yield upper
        yield lower
