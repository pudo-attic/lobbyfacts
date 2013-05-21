import logging

from nomenklatura import Dataset, Entity

from lobbyfacts.core import app

log = logging.getLogger(__name__)

DATASET_CACHE = {}
NAME_CACHE = {}

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
        DATASET_CACHE[dataset] = Dataset(dataset,
            host=app.config.get('NOMENKLATURA_URL'),
            api_key=app.config.get('NOMENKLATURA_APIKEY'))
        for entity in DATASET_CACHE[dataset].entities():
            NAME_CACHE[(dataset, entity.name.lower())] = entity
        for alias in DATASET_CACHE[dataset].aliases():
            if alias.is_invalid:
                NAME_CACHE[(dataset, alias.name.lower())] = \
                    Dataset.Invalid({'dataset': alias.dataset, 'name': alias.name})
            elif alias.is_matched:
                NAME_CACHE[(dataset, alias.name.lower())] = \
                    Entity(DATASET_CACHE[dataset], alias.entity)
    return DATASET_CACHE[dataset]


def canonical(dataset, value, context={}, readonly=False):
    lvalue = value.lower()
    if not (dataset, lvalue) in NAME_CACHE:
        try:
            ds = get_dataset(dataset)
            value = clean_value(value)
            v = ds.lookup(value, context=context,
                          readonly=readonly)
            NAME_CACHE[(dataset, lvalue)] = v
        except Dataset.Invalid, ex:
            NAME_CACHE[(dataset, lvalue)] = ex
        except Dataset.NoMatch, ex:
            NAME_CACHE[(dataset, lvalue)] = ex

    res = NAME_CACHE[(dataset, lvalue)]
    log.debug(" - %s :> %s", value, res)
    if isinstance(res, Dataset.Invalid):
        return None
    if isinstance(res, Dataset.NoMatch):
        raise ValueError("%s: no match." % value)
    return res.name

