import logging

from lobbyfacts.core import db
from lobbyfacts.data import etl_engine
from lobbyfacts.data.lib.countries import get_countries
from lobbyfacts.model import Country

log = logging.getLogger(__name__)

def make_countries(engine):
    log.debug("Create country reference data in production...")
    for country in get_countries():
        data = {'code': country.get('iso2').strip(),
                'name': country.get('country')}
        if not data['code']:
            continue
        country = Country.by_code(data['code'])
        if country is None:
            country = Country.create(data)
        else:
            country.update(data)
    db.session.commit()

def load(engine):
    make_countries(engine)

if __name__ == '__main__':
    engine = etl_engine()
    load(engine)

