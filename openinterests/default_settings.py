
DEBUG = True
CACHE = False
SECRET_KEY = 'no'
SITE_TITLE = 'openinterests.eu'
#SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/openinterests'
SQLALCHEMY_DATABASE_URI = 'sqlite:///local.db'

NOMENKLATURA_URL = 'http://nomenklatura.okfnlabs.org'
NOMENKLATURA_APIKEY = None

ETL_URL = 'sqlite:///etl.db'
ETL_URL = 'postgresql://localhost/openinterests_etl'

ETL_PYBOSSA_HOST = 'http://pybossa.com'
ETL_PYBOSSA_KEY = None # fill in from http://pybossa.com/account/profile


