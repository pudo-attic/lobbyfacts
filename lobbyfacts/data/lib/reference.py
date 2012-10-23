from nkclient import NKDataset, NKInvalid, NKNoMatch

from lobbyfacts.core import app

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
    return DATASET_CACHE[dataset]

def canonical(dataset, value, context={}):
    if not (dataset, value) in VALUE_CACHE:
        try:
            ds = get_dataset(dataset)
            value = clean_value(value)
            v = ds.lookup(value, context=context)
            VALUE_CACHE[(dataset, value)] = v.value
        except NKInvalid, ex:
            VALUE_CACHE[(dataset, value)] = ex
        except NKNoMatch, ex:
            VALUE_CACHE[(dataset, value)] = ex

    res = VALUE_CACHE[(dataset,value)]
    if isinstance(res, NKInvalid):
        return None
    if isinstance(res, NKNoMatch):
        raise ValueError("%s: no match." % value)
    return res

