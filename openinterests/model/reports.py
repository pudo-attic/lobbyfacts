from openinterests.core import db

from openinterests.model.entity import Entity

def test_report():
    """ Just a test for debugging reports. """
    return db.session.query(Entity.id.label('id'),
        Entity.name.label('name'))
    return db.session.query(Entity)




