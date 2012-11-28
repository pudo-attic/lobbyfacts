from lobbyfacts.core import db
from lobbyfacts.model.api import ApiEntityMixIn
from lobbyfacts.model.revision import RevisionedMixIn
from lobbyfacts.model.entity import Entity
from lobbyfacts.model.representative import Representative

class Person(db.Model, RevisionedMixIn, ApiEntityMixIn):
    __tablename__ = 'person'

    entity_id = db.Column(db.String(36), db.ForeignKey('entity.id'))

    title = db.Column(db.Unicode)
    first_name = db.Column(db.Unicode)
    last_name = db.Column(db.Unicode)
    position = db.Column(db.Unicode)


    def update_values(self, data):
        self.entity = data.get('entity')

        self.title = data.get('title')
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.position = data.get('position')

    @classmethod
    def by_name(cls, name):
        q = db.session.query(cls)
        q = q.join(Entity)
        q = q.filter(Entity.name==name)
        return q.first()

    def as_shallow(self):
        d = super(Person, self).as_dict()
        d.update({
            'uri': self.uri,
            'name': self.entity.name if self.entity else None,
            'title': self.title,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'position': self.position
            })
        return d

    def as_dict(self):
        d = self.as_shallow()
        d.update({
            'entity': self.entity.as_shallow() if self.entity else None,
            'accreditations': [a.as_dict(person=False) for a in self.accreditations],
            'representatives_head': [r.as_shallow() for r in self.representatives_head],
            'representatives_legal': [r.as_shallow() for r in self.representatives_legal]
            })
        return d

    def __repr__(self):
        return "<Person(%s,%r)>" % (self.id, self.entity)


Entity.person = db.relationship(Person,
        uselist=False,
        backref=db.backref('entity'))


Person.representatives_head = db.relationship('Representative', 
            primaryjoin=Representative.head_id==Person.id,
            #foreign_keys=[Person.id],
            lazy='dynamic',
            backref=db.backref('head',
                uselist=False,
                primaryjoin=Representative.head_id==Person.id,
                ))


Person.representatives_legal = db.relationship('Representative', 
            primaryjoin=Representative.legal_id==Person.id,
            #foreign_keys=[Person.id],
            lazy='dynamic',
            backref=db.backref('legal',
                uselist=False,
                primaryjoin=Representative.legal_id==Person.id
                ))


class Accreditation(db.Model, RevisionedMixIn, ApiEntityMixIn):
    __tablename__ = 'accreditation'

    representative_id = db.Column(db.String(36), db.ForeignKey('representative.id'))
    person_id = db.Column(db.String(36), db.ForeignKey('person.id'))

    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    def update_values(self, data):
        self.representative = data.get('representative')
        self.person = data.get('person')

        self.start_date = data.get('start_date')
        self.end_date = data.get('end_date')

    @classmethod
    def by_rp(cls, person, representative):
        q = db.session.query(cls)
        q = q.filter(cls.person_id==person.id)
        q = q.filter(cls.representative_id==representative.id)
        return q.first()

    def as_dict(self, person=True, representative=True):
        d = super(Accreditation, self).as_dict()
        d.update({
            'uri': self.uri,
            'start_date': self.start_date,
            'end_date': self.end_date
            })
        if person:
            d['person'] = self.person.as_shallow()
        if representative:
            d['representative'] = self.representative.as_shallow()
        return d

    def __repr__(self):
        return "<Accreditation(%s,%r,%r)>" % (self.id, self.representative, self.person)


Accreditation.person = db.relationship(Person,
        #primaryjoin=db.and_(Person.id == Accreditation.person_id,
        #                    Person.serial == Accreditation.person_serial),
        uselist=False,
        backref=db.backref('accreditations'))

Accreditation.representative = db.relationship(Representative,
        #primaryjoin=db.and_(Representative.id == Accreditation.representative_id,
        #                    Representative.serial == Accreditation.representative_serial),
        uselist=False,
        backref=db.backref('accreditations'))

