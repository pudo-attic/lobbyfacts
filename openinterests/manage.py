from flaskext.script import Manager

from openinterests.core import app, db
from openinterests.model import *
from openinterests import web

manager = Manager(app)

@manager.command
def createdb():
    """ Create the SQLAlchemy database. """
    db.create_all()


def goldfish():
    org = Organisation.create({'name': "BLA"})
    id = org.id
    print org
    db.session.commit()
    org = Organisation.by_id(id)
    org.update({'name': "FOO"})
    print org
    db.session.commit()
    org = Organisation.by_id(org.id)
    org.update({'name': "FOO"})
    print org
    db.session.commit()


if __name__ == '__main__':
    manager.run()
