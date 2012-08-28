
from openinterests.core import app
from openinterests.views.api import make_entity_api
from openinterests.model import Entity, Country, Representative, Organisation

API_PREFIX = '/api/1'

app.register_blueprint(make_entity_api(Entity), url_prefix=API_PREFIX)
app.register_blueprint(make_entity_api(Country), url_prefix=API_PREFIX)
app.register_blueprint(make_entity_api(Representative), url_prefix=API_PREFIX)
app.register_blueprint(make_entity_api(Organisation), url_prefix=API_PREFIX)

