import logging
import csv
import os
import sys

from nkclient import NKDataset, NKNoMatch, NKInvalid, NKException

log = logging.getLogger('load')


def update_entities(file_name, host_name, api_key, skip=0):
    ds = NKDataset('openinterests-entities',
            host=host_name,
            api_key=api_key)
    log.info("Updating nomenklatura: %s", file_name)
    if os.path.exists(file_name):
        fh = open(file_name, 'rb')
        reader = csv.DictReader(fh)
        for i, d in enumerate(reader):
            if i < skip:
                continue
            e = [(k, v.decode('utf-8')) for (k, v) in d.items()]
            e = dict(e)
            make_link(ds, e)
        fh.close()

def make_link(ds, e):
    if not len(e['canonicalName']) or \
        e['etlFingerPrint'] == e['canonicalName']:
        return
    log.info("Updating: %s -> %s", e['etlFingerPrint'], e['canonicalName'])
    try:
        v = ds.ensure_value(e['canonicalName'], data={
            'table': e['etlTable'],
            'countryCode': e['countryCode'],
            'legalStatus': e['legalStatus']
            })
    except NKException, ex:
        log.warning("Error: %s", ex)
        return
    try:
        ds.lookup(e['etlFingerPrint'])
    except NKNoMatch, nm:
        ds.match(nm.id, v.id)
    except NKInvalid, inv:
        log.exception(inv)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    assert 'NOMENKLATURA_APIKEY' in os.environ, \
        'Need to set NOMENKLATURA_APIKEY environment variable first!'
    api_key = os.environ.get('NOMENKLATURA_APIKEY')
    update_entities('entities.csv', 'http://nomenklatura.okfnlabs.org', api_key, 
                    skip=0)
