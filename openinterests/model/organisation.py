from datetime import datetime

from openinterests.core import db
from openinterests.model.revision import RevisionedMixIn
from openinterests.model import util

class Organisation(db.Model, RevisionedMixIn):
    __tablename__ = 'organisation'

    id = db.Column(db.String(36), primary_key=True, default=util.make_id)
    serial = db.Column(db.BigInteger, primary_key=True, default=util.make_serial)
    current = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    name = db.Column(db.Unicode)


    def update_values(self, data):
        self.name = data.get('name')

    def __repr__(self):
        return "<Organisation(%s,%s)>" % (self.id, self.name)

