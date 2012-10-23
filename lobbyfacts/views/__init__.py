
from openinterests.core import app
from openinterests.views.api import make_entity_api
from openinterests.views.reports import reports
from openinterests.model import Entity, Country, Representative, Organisation
from openinterests.model import Person, Category, Accreditation, OrganisationMembership
from openinterests.model import FinancialData, FinancialTurnover

API_PREFIX = '/api/1'

for e in [Entity, Person, Category, Country, Representative, Organisation,
          Accreditation, OrganisationMembership, FinancialData, FinancialTurnover]:
    app.register_blueprint(make_entity_api(e), url_prefix=API_PREFIX)

app.register_blueprint(reports, url_prefix=API_PREFIX)
