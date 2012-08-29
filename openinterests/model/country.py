from datetime import datetime

from openinterests.core import db
from openinterests.model.api import ApiEntityMixIn
from openinterests.model.revision import RevisionedMixIn
from openinterests.model import util
from openinterests.model.representative import Representative

class Country(db.Model, ApiEntityMixIn):
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

    @classmethod
    def by_id(cls, id):
        q = db.session.query(cls)
        q = q.filter_by(id=id)
        return q.first()

    @classmethod
    def all(cls):
        return db.session.query(cls)

    def as_shallow(self):
        return {
            'uri': self.uri,
            'code': self.code,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
            }

    def as_dict(self):
        d = self.as_shallow()
        #d.update({
        #    'representatives': self.representatives
        #    })
        return d

    def __repr__(self):
        return "<Country(%s)>" % (self.code)


class CountryMembership(db.Model, RevisionedMixIn, ApiEntityMixIn):
    __tablename__ = 'country_membership'

    representative_id = db.Column(db.String(36), db.ForeignKey('representative.id'))
    country_id = db.Column(db.String(36), db.ForeignKey('country.id'))

    def update_values(self, data):
        self.representative = data.get('representative')
        self.country = data.get('country')

    @classmethod
    def by_rpc(cls, representative, country):
        q = db.session.query(cls)
        q = q.filter_by(current=True)
        q = q.filter(cls.country_id==country.id)
        q = q.filter(cls.representative_id==representative.id)
        return q.first()

    def __repr__(self):
        return "<CountryMembership(%s,%r)>" % (self.id, self.country)

CountryMembership.country = db.relationship(Country,
            primaryjoin=Country.id == CountryMembership.country_id,
            backref=db.backref('memberships',
                lazy='dynamic',
                primaryjoin=db.and_(Country.id == CountryMembership.country_id,
                                    CountryMembership.current == True)
            ))

CountryMembership.representative = db.relationship(Representative,
        primaryjoin=db.and_(Representative.id == CountryMembership.representative_id,
                            Representative.current == True),
        uselist=False,
        backref=db.backref('country_memberships',
            lazy='dynamic',
            primaryjoin=db.and_(Representative.id == CountryMembership.representative_id,
                                CountryMembership.current == True),
            ))


