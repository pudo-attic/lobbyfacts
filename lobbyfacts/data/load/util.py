import logging

from lobbyfacts.model import Entity, Person, Organisation

log = logging.getLogger(__name__)

def to_integer(val):
    if val is None:
        return None
    try:
        return int(float(val))
    except ValueError:
        return None

def to_float(val):
    if val is None:
        return None
    try:
        return float(val)
    except ValueError:
        return None

def upsert_entity(canonical_name, name=None, suffix=None, **kw):
    if canonical_name is None or not len(canonical_name.strip()):
        canonical_name = name
    if suffix is not None and len(suffix):
        canonical_name = "%s %s" % (canonical_name, suffix)
    kw['name'] = canonical_name
    entity = Entity.by_name(canonical_name)
    if canonical_name != name:
        entity_ = Entity.by_name(name)
        if entity_ is not None:
            if entity is None:
                entity = entity_
                entity_.update(kw)
            else:
                entity_.delete()
    if entity is None:
        entity = Entity.create(kw)
    return entity

def upsert_person(data):
    entity = upsert_entity(data.get('canonical_name'), data.get('name'))
    data['entity'] = entity
    person = Person.by_name(entity.name)
    if person is None:
        person = Person.create(data)
    else:
        person.update(data)
    return person

def upsert_organisation(data):
    entity = upsert_entity(data.get('canonical_name'), data.get('name'))
    data['entity'] = entity
    organisation = Organisation.by_name(entity.name)
    if organisation is None:
        organisation = Organisation.create(data)
    else:
        organisation.update(data)
    return organisation


