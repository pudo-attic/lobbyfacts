from datetime import datetime

from openinterests.core import db
from openinterests.model.api import ApiEntityMixIn
from openinterests.model.revision import RevisionedMixIn
from openinterests.model import util
from openinterests.model.entity import Entity
from openinterests.model.representative import Representative


class Organisation(db.Model, RevisionedMixIn, ApiEntityMixIn):
    __tablename__ = 'organisation'

    entity_id = db.Column(db.String(36), db.ForeignKey('entity.id'))
    number_of_members = db.Column(db.Integer, nullable=True)


    def update_values(self, data):
        self.entity = data.get('entity')
        self.number_of_members = data.get('number_of_members')

    @classmethod
    def by_name(cls, name):
        q = db.session.query(cls)
        q = q.join(Entity)
        q = q.filter_by(current=True)
        q = q.filter(Entity.name==name)
        return q.first()

    def as_shallow(self):
        d = super(Organisation, self).as_dict()
        d.update({
            'uri': self.uri,
            'name': self.entity.name,
            'number_of_members': self.number_of_members
            })
        return d

    def as_dict(self):
        d = self.as_shallow()
        d.update({
            'entity': self.entity.as_shallow(),
            'memberships': [m.as_dict(organisation=False) for m in self.memberships]
            })
        return d

    def __repr__(self):
        return "<Organisation(%s,%r)>" % (self.id, self.entity)


Entity.organisation = db.relationship(Organisation,
        primaryjoin=db.and_(Entity.id == Organisation.entity_id,
                            Entity.current == True),
        uselist=False,
        backref=db.backref('entity'))


class OrganisationMembership(db.Model, RevisionedMixIn, ApiEntityMixIn):
    __tablename__ = 'organisation_membership'

    organisation_id = db.Column(db.String(36), db.ForeignKey('organisation.id'))
    representative_id = db.Column(db.String(36), db.ForeignKey('representative.id'))

    def update_values(self, data):
        self.organisation = data.get('organisation')
        self.representative = data.get('representative')

    @classmethod
    def by_rpo(cls, representative, organisation):
        q = db.session.query(cls)
        q = q.filter_by(current=True)
        q = q.filter(cls.representative_id==representative.id)
        q = q.filter(cls.organisation_id==organisation.id)
        return q.first()

    def as_dict(self, organisation=True, representative=True):
        d = super(OrganisationMembership, self).as_dict()
        d.update({
            'uri': self.uri,
            })
        if organisation:
            d['organisation'] = self.organisation.as_shallow()
        if representative:
            d['representative'] = self.representative.as_shallow()
        return d


    def __repr__(self):
        return "<Organisation(%s,%r)>" % (self.id, self.entity)

OrganisationMembership.organisation = db.relationship(Organisation,
        primaryjoin=db.and_(Organisation.id == OrganisationMembership.organisation_id,
                            Organisation.current == True),
        uselist=False,
        backref=db.backref('memberships',
            lazy='dynamic',
            primaryjoin=db.and_(Organisation.id == OrganisationMembership.organisation_id,
                                OrganisationMembership.current == True),
            ))

OrganisationMembership.representative = db.relationship(Representative,
        primaryjoin=db.and_(Representative.id == OrganisationMembership.representative_id,
                            Representative.current == True),
        uselist=False,
        backref=db.backref('organisation_memberships',
            lazy='dynamic',
            primaryjoin=db.and_(Representative.id == OrganisationMembership.representative_id,
                                OrganisationMembership.current == True),
            ))

