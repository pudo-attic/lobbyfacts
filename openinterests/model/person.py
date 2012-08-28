from openinterests.core import db
from openinterests.model.api import ApiEntityMixIn
from openinterests.model.revision import RevisionedMixIn
from openinterests.model.entity import Entity
from openinterests.model.representative import Representative

class Person(db.Model, RevisionedMixIn, ApiEntityMixIn):
    __tablename__ = 'person'

    entity_id = db.Column(db.String(36), db.ForeignKey('entity.id'))

    title = db.Column(db.Unicode)
    first_name = db.Column(db.Unicode)
    last_name = db.Column(db.Unicode)
    position = db.Column(db.Unicode)


    def update_values(self, data):
        self.entity_id = data.get('entity').id

        self.title = data.get('title')
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.position = data.get('position')

    @classmethod
    def by_name(cls, name):
        q = db.session.query(cls)
        q = q.join(Entity)
        q = q.filter_by(current=True)
        q = q.filter(Entity.name==name)
        return q.first()

    def __repr__(self):
        return "<Person(%s,%r)>" % (self.id, self.entity)


Entity.person = db.relationship(Person,
        primaryjoin=db.and_(Entity.id == Person.entity_id,
                            Entity.current == True),
        uselist=False,
        backref=db.backref('entity'))


Person.representatives_head = db.relationship('Representative', 
            primaryjoin=db.and_(Representative.head_id==Person.id,
                                Representative.current==True),
            foreign_keys=[Person.id],
            lazy='dynamic',
            backref=db.backref('head',
                uselist=False,
                primaryjoin=db.and_(Representative.head_id==Person.id,
                                    Person.current==True)
                ))


Person.representatives_legal = db.relationship('Representative', 
            primaryjoin=db.and_(Representative.legal_id==Person.id,
                                Representative.current==True),
            foreign_keys=[Person.id],
            lazy='dynamic',
            backref=db.backref('legal',
                uselist=False,
                primaryjoin=db.and_(Representative.legal_id==Person.id,
                                    Person.current==True)
                ))


class Accreditation(db.Model, RevisionedMixIn, ApiEntityMixIn):
    __tablename__ = 'accreditation'

    representative_id = db.Column(db.String(36), db.ForeignKey('representative.id'))
    person_id = db.Column(db.String(36), db.ForeignKey('person.id'))

    def update_values(self, data):
        self.representative_id = data.get('representative').id
        self.person_id = data.get('person').id

        self.start_date = data.get('start_date')
        self.end_date = data.get('end_date')

    @classmethod
    def by_rp(cls, person, representative):
        q = db.session.query(cls)
        q = q.filter_by(current=True)
        q = q.filter(cls.person_id==person.id)
        q = q.filter(cls.representative_id==representative.id)
        return q.first()

    def __repr__(self):
        return "<Accreditation(%s,%r)>" % (self.id, self.entity)


Accreditation.person = db.relationship(Person,
        primaryjoin=db.and_(Person.id == Accreditation.person_id,
                            Person.current == True),
        uselist=False,
        backref=db.backref('person'))

Accreditation.representative = db.relationship(Representative,
        primaryjoin=db.and_(Representative.id == Accreditation.representative_id,
                            Representative.current == True),
        uselist=False,
        backref=db.backref('representative'))

