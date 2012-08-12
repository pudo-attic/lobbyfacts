from datetime import datetime
import logging
from lxml import etree
from pprint import pprint

import requests

from openinterests.data import sl, etl_engine

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
            'orgIdentificationCode': ap_el.findtext(NS + 'orgIdentificationCode'),
            'numberOfIR': ap_el.findtext(NS + 'numberOfIR'),
            'orgName': ap_el.findtext(NS + 'orgName'),
            'title': ap_el.findtext(NS + 'title'),
            'firstName': ap_el.findtext(NS + 'firstName'),
            'lastName': ap_el.findtext(NS + 'lastName'),
            'accreditationStartDate': dateconv(ap_el.findtext(NS + 'accreditationStartDate')),
            'accreditationEndDate': dateconv(ap_el.findtext(NS + 'accreditationEndDate')),
            }
        yield ap

def save(person, engine):
    table = sl.get_table(engine, 'person')
    orgs = list(sl.find(engine, sl.get_table(engine, 'representative'),
                   identificationCode=person['orgIdentificationCode']))
    if len(orgs):
        org = max(orgs, key=lambda o: o['lastUpdateDate'])
        person['representativeEtlId'] = org['etlId']
        person['role'] = 'accredited'
        name = '%s %s %s' % (person['title'] or '',
                             person['firstName'],
                             person['lastName'])
        person['name'] = name.strip()
        log.debug("Accreditation: %s", name)
        sl.upsert(engine, table, person,
            ['representativeEtlId', 'role', 'name'])
    else:
        log.warn("Cannot associate with a registered interest: %r", person)

def extract_data(engine, data):
    log.info("Extracting accredditation data from %s", data)
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

