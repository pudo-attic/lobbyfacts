from pprint import pprint
import logging

from lobbyfacts.data import sl, etl_engine
from lobbyfacts.data.lib.reference import canonical
from lobbyfacts.data.lib.countries import country_by_name

log = logging.getLogger(__name__)

DATASET = 'openinterests-entities'

def map_names(map_func, engine, table_name, source_column='name',
        out_column='canonical_name', **kw):
    table = sl.get_table(engine, table_name)
    seen_values = set()
    log.info("Normalising names on '%s', column '%s'...", table_name,
             source_column)
    for row in sl.find(engine, table):
        value = row.get(source_column)
        if value in seen_values:
            continue
        seen_values.add(value)
        d = {source_column: value, 'etl_clean': True,
             out_column: None}
        try:
            out = map_func(value, row, **kw)
            if out is None:
                d['etl_clean'] = False
            else:
                d[out_column] = out
        except ValueError, ve:
            d['etl_clean'] = False
        sl.upsert(engine, table, d, [source_column])

def transform(engine):
    countries_func = lambda v, c: country_by_name(v).get('iso2')
    map_names(countries_func, engine, 'representative',
            'contact_country', 'country_code')
    map_names(countries_func, engine, 'country_of_member',
            'country', 'country_code')
    map_names(countries_func, engine, 'expertgroup_member_country',
            'country', 'country_code')

    names_func = lambda v, c: canonical(DATASET, v, context=c)
    map_names(names_func, engine, 'representative')
    #map_names(names_func, engine, 'person')
    map_names(names_func, engine, 'financial_data_turnover')
    map_names(names_func, engine, 'organisation', readonly=True)
    map_names(names_func, engine, 'network_entity', readonly=True)
    map_names(names_func, engine, 'expertgroup_member', readonly=True)


if __name__ == '__main__':
    engine = etl_engine()
    transform(engine)

