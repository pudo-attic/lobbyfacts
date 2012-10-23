import logging
from pprint import pprint

from lobbyfacts.core import db
from lobbyfacts.data import sl, etl_engine
from lobbyfacts.model import Entity, Representative, Country, Category
from lobbyfacts.model import Organisation, OrganisationMembership, Person
from lobbyfacts.model import Accreditation, FinancialData, FinancialTurnover
from lobbyfacts.model import CountryMembership
from lobbyfacts.data.load.util import to_integer, upsert_person
from lobbyfacts.data.load.util import upsert_person, upsert_organisation, upsert_entity

log = logging.getLogger(__name__)

def upsert_category(id, name, parent=None):
    data = {'id': id, 'name': name, 'parent': parent}
    category = Category.by_id(id)
    if category is None:
        category = Category.create(data)
    else:
        category.update(data)
    return category

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
        financial_data = FinancialData.by_rsd(representative, fd.get('start_date'))
        if financial_data is None:
            financial_data = FinancialData.create(fd)
        else:
            financial_data.update(fd)

        for turnover_ in sl.find(engine, sl.get_table(engine, 'financial_data_turnover'),
                representative_etl_id=rep['etl_id'], financial_data_etl_id=fd['etl_id']):
            if turnover_.get('etl_clean') is False:
                continue
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

    for org in sl.find(engine, sl.get_table(engine, 'organisation'),
            representative_etl_id=rep['etl_id']):
        if org.get('etl_clean') is False:
            continue
        org['number_of_members'] = to_integer(org['number_of_members'])
        organisation = upsert_organisation(org)
        omdata = {'representative': representative, 'organisation': organisation}
        om = OrganisationMembership.by_rpo(representative, organisation)
        if om is None:
            om = OrganisationMembership.create(omdata)
        else:
            om.update(omdata)

    for country_ in sl.find(engine, sl.get_table(engine, 'country_of_member'),
            representative_etl_id=rep['etl_id']):
        if country_.get('etl_clean') is False:
            continue
        cdata = {'representative': representative,
                 'country': Country.by_code(country_.get('country_code'))}
        cm = CountryMembership.by_rpc(representative, cdata.get('country'))
        if cm is None:
            cm = CountryMembership.create(cdata)
        else:
            cm.update(cdata)

    db.session.commit()


def load(engine):
    for rep in sl.all(engine, sl.get_table(engine, 'representative')):
        log.info("Loading: %s", rep.get('name'))
        if rep['etl_clean'] is False:
            log.debug("Skipping!")
            continue
        load_representative(engine, rep)

if __name__ == '__main__':
    engine = etl_engine()
    load(engine)

