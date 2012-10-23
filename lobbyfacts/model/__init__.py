
from openinterests.model.entity import Entity
from openinterests.model.representative import Representative
from openinterests.model.country import Country, CountryMembership
from openinterests.model.category import Category
from openinterests.model.person import Person, Accreditation
from openinterests.model.organisation import Organisation, OrganisationMembership
from openinterests.model.financial_data import FinancialData, FinancialTurnover

from openinterests.model.reports import test_report, rep_by_exp, rep_by_country
from openinterests.model.reports import rep_by_turnover, rep_by_fte, fte_by_subcategory

REPORTS = {
    'test_report': test_report,
    'rep_by_exp': rep_by_exp,
    'rep_by_country': rep_by_country,
    'rep_by_turnover': rep_by_turnover,
    'rep_by_fte': rep_by_fte,
    'fte_by_subcategory': fte_by_subcategory
    }
