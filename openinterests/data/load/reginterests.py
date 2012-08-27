import logging
from pprint import pprint

from openinterests.core import db
from openinterests.data import sl, etl_engine
from openinterests.model import Entity, Representative, Country, Category, Person, Accreditation, FinancialData, FinancialTurnover
from openinterests.data.lib.countries import get_countries

log = logging.getLogger(__name__)

def to_integer(val):
    if val is None:
        return None
    try:
        return int(float(val))
    except ValueError:
        return None

def upsert_entity(canonical_name, name=None, **kw):
    if canonical_name is None or not len(canonical_name.strip()):
        canonical_name = name
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

def upsert_category(id, name, parent=None):
    data = {'id': id, 'name': name, 'parent': parent}
    category = Category.by_id(id)
    if category is None:
        category = Category.create(data)
    else:
        category.update(data)
    return category

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


def load_representative(engine, rep):
    entity = upsert_entity(rep.get('canonical_name'), 
                name=rep.get('original_name'), 
                acronym=rep.get('acronym'))
    rep['entity'] = entity
    rep['members'] = to_integer(rep['members'])
    rep['number_of_natural_persons'] = to_integer(rep['number_of_natural_persons'])
    rep['number_of_organisations'] = to_integer(rep['number_of_organisations'])

    rep['contact_phone'] = " ".join((rep.get('contact_indic_phone') or '', rep.get('contact_phone') or '')).strip()
    rep['contact_fax'] = " ".join((rep.get('contact_indic_fax') or '', rep.get('contact_fax') or '')).strip()
    rep['contact_country'] = Country.by_code(rep['country_code'])

    main_category = upsert_category(rep.get('main_category_id'),
                                    rep.get('main_category'))
    rep['main_category'] = main_category
    rep['sub_category'] = upsert_category(rep.get('sub_category_id'),
                                          rep.get('sub_category'),
                                          main_category)

    accreditations = []
    for person_data in sl.find(engine, sl.get_table(engine, 'person'),
            representative_etl_id=rep['etl_id']):
        person = upsert_person(person_data)
        if person_data.get('role') == 'head':
            rep['head'] = person
        if person_data.get('role') == 'legal':
            rep['legal'] = person
        if person_data.get('role') == 'accredited':
            accreditations.append((person, person_data))

    representative = Representative.by_identification_code(rep['identification_code'])
    if representative is None:
        representative = Representative.create(rep)
    else:
        representative.update(rep)

    for person, data_ in accreditations:
        data_['person'] = person
        data_['representative'] = representative
        accreditation = Accreditation.by_rp(person, representative)
        if accreditation is None:
            accreditation = Accreditation.create(data_)
        else:
            accreditation.update(data_)

    for fd in sl.find(engine, sl.get_table(engine, 'financial_data'),
            representative_etl_id=rep['etl_id']):
        fd['turnover_min'] = to_integer(fd.get('turnover_min'))
        fd['turnover_max'] = to_integer(fd.get('turnover_max'))
        fd['turnover_absolute'] = to_integer(fd.get('turnover_absolute'))
        fd['cost_min'] = to_integer(fd.get('cost_min'))
        fd['cost_max'] = to_integer(fd.get('cost_max'))
        fd['cost_absolute'] = to_integer(fd.get('cost_absolute'))
        fd['direct_fd_costs_min'] = to_integer(fd.get('direct_fd_costs_min'))
        fd['direct_fd_costs_max'] = to_integer(fd.get('direct_fd_costs_max'))
        fd['total_budget'] = to_integer(fd.get('total_budget'))
        fd['public_financing_total'] = to_integer(fd.get('public_financing_total'))
        fd['public_financing_infranational'] = to_integer(fd.get('public_financing_infranational'))
        fd['public_financing_national'] = to_integer(fd.get('public_financing_national'))
        fd['eur_sources_grants'] = to_integer(fd.get('eur_sources_grants'))
        fd['eur_sources_procurement'] = to_integer(fd.get('eur_sources_procurement'))
        fd['other_sources_donation'] = to_integer(fd.get('other_sources_donation'))
        fd['other_sources_contributions'] = to_integer(fd.get('other_sources_donation'))
        fd['other_sources_total'] = to_integer(fd.get('other_sources_total'))
        fd['representative'] = representative
        financial_data = FinancialData.by_rsd(representative, fd.get('start_end'))
        if financial_data is None:
            financial_data = FinancialData.create(fd)
        else:
            financial_data.update(fd)

        for turnover_ in sl.find(engine, sl.get_table(engine, 'financial_data_turnover'),
                financial_data_etl_id=fd['etl_id']):
            turnover_['entity'] = upsert_entity(turnover_.get('canonical_name'),
                                                turnover_.get('name'))
            turnover_['financial_data'] = financial_data
            turnover_['min'] = to_integer(turnover_.get('min'))
            turnover_['max'] = to_integer(turnover_.get('max'))
            turnover = FinancialTurnover.by_fde(financial_data, turnover_['entity'])
            if turnover is None:
                turnover = FinancialTurnover.create(turnover_)
            else:
                turnover.update(turnover_)

    db.session.commit()


def load(engine):
    make_countries(engine)
    for rep in sl.all(engine, sl.get_table(engine, 'representative')):
        log.info("Loading: %s", rep.get('name'))
        if rep['etl_clean'] is False:
            log.debug("Skipping!")
            continue
        load_representative(engine, rep)

if __name__ == '__main__':
    engine = etl_engine()
    load(engine)
