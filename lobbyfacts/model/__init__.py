import logging

from lobbyfacts.model.entity import Entity
from lobbyfacts.model.representative import Representative
from lobbyfacts.model.country import Country, CountryMembership
from lobbyfacts.model.category import Category
from lobbyfacts.model.person import Person, Accreditation
from lobbyfacts.model.organisation import Organisation, OrganisationMembership
from lobbyfacts.model.financial_data import FinancialData, FinancialTurnover

from lobbyfacts.model.reports import test_report, rep_by_exp, rep_by_country
from lobbyfacts.model.reports import representatives, places
from lobbyfacts.model.reports import rep_by_turnover, rep_by_fte, fte_by_subcategory

log = logging.getLogger(__name__)

REPORTS = {
    'test_report': test_report,
    'places': places,
    'representatives': representatives,
    'rep_by_exp': rep_by_exp,
    'rep_by_country': rep_by_country,
    'rep_by_turnover': rep_by_turnover,
    'rep_by_fte': rep_by_fte,
    'fte_by_subcategory': fte_by_subcategory
    }

def update_index():
    from lobbyfacts.core import db
    for entity in db.session.query(Entity).yield_per(1000):
        log.info("Indexing %s...", entity.name)
        entity.update_index()
        #db.session.add(entity)
    db.session.commit()
