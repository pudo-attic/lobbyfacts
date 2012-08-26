from datetime import datetime

from openinterests.core import db
from openinterests.model.revision import RevisionedMixIn
from openinterests.model import util


class Organisation(db.Model, RevisionedMixIn):
    __tablename__ = 'organisation'

    name = db.Column(db.Unicode)

    def update_values(self, data):
        self.name = data.get('name')

    def __repr__(self):
        return "<Organisation(%s,%s)>" % (self.id, self.name)

