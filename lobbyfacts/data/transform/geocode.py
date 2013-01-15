import logging
import requests

from pprint import pprint

from lobbyfacts.data import sl, etl_engine

log = logging.getLogger(__name__)

URL = "http://nominatim.openstreetmap.org/search"
URL = "http://open.mapquestapi.com/nominatim/v1/search.php"

def transform(engine):
    log.info("Geo-coding representatives...")
    table = sl.get_table(engine, 'representative')
    for row in sl.all(engine, table):
        out = {'id': row['id']}
        if row.get('contact_lon'):
            continue
        query = {
            'format': 'json',
            'limit': 1,
            'city': row.get('contact_town'),
            'street': row.get('contact_street'),
            'country': row.get('contact_country'),
            'postalcode': row.get('contact_post_code')
            }
        response = requests.get(URL, params=query)
        json = response.json()
        if json and len(json):
            geo = json[0]
            log.info("%s @ %s", row.get('name'), geo.get('display_name'))
            out['contact_geoname'] = geo.get('display_name')
            out['contact_lon'] = geo.get('lon')
            out['contact_lat'] = geo.get('lat')
            sl.upsert(engine, table, out, ['id'])

if __name__ == '__main__':
    engine = etl_engine()
    transform(engine)
