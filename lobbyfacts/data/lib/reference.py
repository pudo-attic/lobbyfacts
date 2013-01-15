import logging

from nkclient import NKDataset, NKInvalid, NKNoMatch, NKValue

from lobbyfacts.core import app

log = logging.getLogger(__name__)

DATASET_CACHE = {}
VALUE_CACHE = {}

def clean_value(value):
    value = value.strip()
    value = value.replace('\t', ' ')
    value = value.replace('\n', ' ')
    value = value.replace('\r', ' ')
    value = value.replace('  ', ' ')
    value = value.replace('  ', ' ')
    value = value.replace('  ', ' ')
    return value

def get_dataset(dataset):
    global DATASET_CACHE
    if dataset not in DATASET_CACHE:
        DATASET_CACHE[dataset] = NKDataset(dataset,
            host=app.config.get('NOMENKLATURA_URL'),
            api_key=app.config.get('NOMENKLATURA_APIKEY'))
        for value in DATASET_CACHE[dataset].values():
            VALUE_CACHE[(dataset, value.value.lower())] = value
        for link in DATASET_CACHE[dataset].links():
            if link.is_invalid:
                VALUE_CACHE[(dataset, link.key.lower())] = \
                    NKInvalid({'dataset': link.dataset, 'key': link.key})
            elif link.is_matched:
                VALUE_CACHE[(dataset, link.key.lower())] = \
                    NKValue(DATASET_CACHE[dataset], link.value)
    return DATASET_CACHE[dataset]

def canonical(dataset, value, context={}):
    lvalue = value.lower()
    if not (dataset, lvalue) in VALUE_CACHE:
        try:
            ds = get_dataset(dataset)
            value = clean_value(value)
            v = ds.lookup(value, context=context)
            VALUE_CACHE[(dataset, lvalue)] = v
        except NKInvalid, ex:
            VALUE_CACHE[(dataset, lvalue)] = ex
        except NKNoMatch, ex:
            VALUE_CACHE[(dataset, lvalue)] = ex

    res = VALUE_CACHE[(dataset,lvalue)]
    log.debug(" - %s :> %s", value, res)
    if isinstance(res, NKInvalid):
        return None
    if isinstance(res, NKNoMatch):
        raise ValueError("%s: no match." % value)
    return res.value

