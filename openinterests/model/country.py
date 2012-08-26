from datetime import datetime

from openinterests.core import db
from openinterests.model import util

class Country(db.Model):
    __tablename__ = 'country'

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.Unicode)
    name = db.Column(db.Unicode)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
            onupdate=datetime.utcnow)

    representatives = db.relationship('Representative', 
            backref='contact_country')

    @classmethod
    def create(cls, data):
        cls = cls()
        return cls.update(data)

    def update(self, data):
        self.code = data.get('code')
        self.name = data.get('name')
        db.session.add(self)
        return self

    @classmethod
    def by_code(cls, code):
        q = db.session.query(cls)
        q = q.filter_by(code=code)
        return q.first()

    def __repr__(self):
        return "<Country(%s)>" % (self.code)

