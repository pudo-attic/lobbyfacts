from flask.ext.script import Manager

from lobbyfacts.core import app, db
from lobbyfacts.model import *
from lobbyfacts import web

manager = Manager(app)

@manager.command
def createdb():
    """ Create the SQLAlchemy database. """
    db.create_all()

@manager.command
def extract():
    """ Extract all data from the respective web sources. """
    from lobbyfacts.data import etl_engine
    engine = etl_engine()
    from lobbyfacts.data.extract.reginterests import extract
    extract(engine)
    from lobbyfacts.data.extract.regaccredit import extract
    extract(engine)
    #from lobbyfacts.data.extract.regexpert import extract
    #extract(engine)

@manager.command
def transform():
    """ Apply simple data transformation and cleansing operations. """
    from lobbyfacts.data import etl_engine
    engine = etl_engine()
    from lobbyfacts.data.transform.categories import transform
    transform(engine)
    #from lobbyfacts.data.transform.pbnetworks import transform
    #transform(engine)
    from lobbyfacts.data.transform.names import transform
    transform(engine)
    from lobbyfacts.data.transform.geocode import transform
    transform(engine)

@manager.command
def load():
    """ Load the data from ETL into the production database. """
    from lobbyfacts.data import etl_engine
    engine = etl_engine()
    from lobbyfacts.data.load.common import load
    load(engine)
    from lobbyfacts.data.load.reginterests import load
    load(engine)
    from lobbyfacts.model import update_index
    update_index()

if __name__ == '__main__':
    manager.run()
