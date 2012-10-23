from datetime import datetime
import logging
from lxml import etree
from pprint import pprint

import requests

from lobbyfacts.data import sl, etl_engine

log = logging.getLogger(__name__)

URL = "http://ec.europa.eu/transparencyregister/public/consultation/statistics.do?action=getLobbyistsXml&fileType=ACCREDITED_PERSONS"
_NS = "http://ec.europa.eu/transparencyregister/accreditedPerson/V1"
NS = '{%s}' % _NS


def dateconv(ds):
    return datetime.strptime(ds, "%Y-%m-%d+%H:%M")

def parse(data):
    doc = etree.fromstring(data.encode('utf-8'))
    for ap_el in doc.findall('.//' + NS + 'accreditedPerson'):
        ap = {
            'org_identification_code': ap_el.findtext(NS + 'orgIdentificationCode'),
            'number_of_ir': ap_el.findtext(NS + 'numberOfIR'),
            'org_name': ap_el.findtext(NS + 'orgName'),
            'title': ap_el.findtext(NS + 'title'),
            'first_name': ap_el.findtext(NS + 'firstName'),
            'last_name': ap_el.findtext(NS + 'lastName'),
            'start_date': dateconv(ap_el.findtext(NS + 'accreditationStartDate')),
            'end_date': dateconv(ap_el.findtext(NS + 'accreditationEndDate')),
            }
        yield ap

def save(person, engine):
    table = sl.get_table(engine, 'person')
    orgs = list(sl.find(engine, sl.get_table(engine, 'representative'),
                   identification_code=person['org_identification_code']))
    if len(orgs):
        org = max(orgs, key=lambda o: o['last_update_date'])
        person['representative_etl_id'] = org['etl_id']
        person['role'] = 'accredited'
        name = '%s %s %s' % (person['title'] or '',
                             person['first_name'] or '',
                             person['last_name'] or '')
        person['name'] = name.strip()
        log.debug("Accreditation: %s", name)
        sl.upsert(engine, table, person,
            ['representative_etl_id', 'role', 'name'])
    else:
        log.warn("Cannot associate with a registered interest: %r", person)

def extract_data(engine, data):
    log.info("Extracting accredditation data...")
    for i, ap in enumerate(parse(data)):
        save(ap, engine)
        if i % 100 == 0:
            log.info("Extracted: %s...", i)

def extract(engine):
    res = requests.get(URL)
    extract_data(engine, res.content.decode('utf-8'))

if __name__ == '__main__':
    engine = etl_engine()
    extract(engine)

