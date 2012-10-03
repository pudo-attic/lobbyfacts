from flaskext.script import Manager

from openinterests.core import app, db
from openinterests.model import *
from openinterests import web

manager = Manager(app)

@manager.command
def createdb():
    """ Create the SQLAlchemy database. """
    db.create_all()

@manager.command
def extract():
    """ Extract all data from the respective web sources. """
    from openinterests.data import etl_engine
    engine = etl_engine()
    from openinterests.data.extract.reginterests import extract
    extract(engine)
    from openinterests.data.extract.regaccredit import extract
    extract(engine)
    from openinterests.data.extract.regexpert import extract
    extract(engine)

@manager.command
def transform():
    """ Apply simple data transformation and cleansing operations. """
    from openinterests.data import etl_engine
    engine = etl_engine()
    from openinterests.data.transform.categories import transform
    transform(engine)
    from openinterests.data.transform.pbnetworks import transform
    transform(engine)
    from openinterests.data.transform.names import transform
    transform(engine)

@manager.command
def load():
    """ Load the data from ETL into the production database. """
    from openinterests.data import etl_engine
    engine = etl_engine()
    from openinterests.data.load.common import load
    load(engine)
    from openinterests.data.load.reginterests import load
    load(engine)

if __name__ == '__main__':
    manager.run()
