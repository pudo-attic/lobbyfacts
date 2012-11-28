from lobbyfacts.core import db
from lobbyfacts.model.api import ApiEntityMixIn
from lobbyfacts.model.revision import RevisionedMixIn
from lobbyfacts.model.entity import Entity


class Representative(db.Model, RevisionedMixIn, ApiEntityMixIn):
    __tablename__ = 'representative'

    entity_id = db.Column(db.String(36), db.ForeignKey('entity.id'))

    identification_code = db.Column(db.Unicode)

    goals = db.Column(db.Unicode)
    activities = db.Column(db.Unicode)
    status = db.Column(db.Unicode)
    networking = db.Column(db.Unicode)
    legal_status = db.Column(db.Unicode)
    code_of_conduct = db.Column(db.Unicode)
    web_site_url = db.Column(db.Unicode)

    members = db.Column(db.BigInteger, nullable=True)
    number_of_natural_persons = db.Column(db.BigInteger, nullable=True)
    number_of_organisations = db.Column(db.BigInteger, nullable=True)

    registration_date = db.Column(db.DateTime)
    last_update_date = db.Column(db.DateTime)

    contact_more = db.Column(db.Unicode)
    contact_town = db.Column(db.Unicode)
    contact_number = db.Column(db.Unicode)
    contact_street = db.Column(db.Unicode)
    contact_phone = db.Column(db.Unicode)
    contact_post_code = db.Column(db.Unicode)
    contact_fax = db.Column(db.Unicode)
    contact_lat = db.Column(db.Float)
    contact_lon = db.Column(db.Float)
    contact_country_id = db.Column(db.BigInteger, db.ForeignKey('country.id'))

    main_category_id = db.Column(db.BigInteger, db.ForeignKey('category.id'))
    sub_category_id = db.Column(db.BigInteger, db.ForeignKey('category.id'))
    head_id = db.Column(db.Unicode(36), db.ForeignKey('person.id'))
    legal_id = db.Column(db.Unicode(36), db.ForeignKey('person.id'))

    def update_values(self, data):
        self.entity = data.get('entity')
        self.identification_code = data.get('identification_code')

        self.goals = data.get('goals')
        self.status = data.get('status')
        self.activities = data.get('activities')
        self.networking = data.get('networking')
        self.code_of_conduct = data.get('code_of_conduct')
        self.web_site_url = data.get('web_site_url')
        self.legal_status = data.get('legal_status')

        self.members = data.get('members')
        self.number_of_natural_persons = data.get('number_of_natural_persons')
        self.number_of_organisations = data.get('number_of_organisations')

        self.registration_date = data.get('registration_date')
        self.last_update_date = data.get('last_update_date')

        self.contact_more = data.get('contact_more')
        self.contact_town = data.get('contact_town')
        self.contact_number = data.get('contact_number')
        self.contact_street = data.get('contact_street')
        self.contact_phone = data.get('contact_phone')
        self.contact_post_code = data.get('contact_post_code')
        self.contact_fax = data.get('contact_fax')
        self.contact_lon = data.get('contact_lon')
        self.contact_lat = data.get('contact_lat')
        self.contact_country = data.get('contact_country')

        self.main_category = data.get('main_category')
        self.sub_category = data.get('sub_category')

        self.head = data.get('head')
        self.legal = data.get('legal')

    @classmethod
    def by_identification_code(cls, identification_code):
        return cls.by_attr(cls.identification_code,
                           identification_code)

    def as_shallow(self):
        d = super(Representative, self).as_dict()
        d.update({
            'uri': self.uri,
            'name': self.entity.name if self.entity else None,
            'identification_code': self.identification_code,
            'goals': self.goals,
            'status': self.status,
            'activities': self.activities,
            'networking': self.networking,
            'code_of_conduct': self.code_of_conduct,
            'web_site_url': self.web_site_url,
            'legal_status': self.legal_status,
            'members': self.members,
            'number_of_natural_persons': self.number_of_natural_persons,
            'number_of_organisations': self.number_of_organisations,
            'registration_date': self.registration_date,
            'last_update_date': self.last_update_date,
            'contact_more': self.contact_more,
            'contact_town': self.contact_town,
            'contact_number': self.contact_number,
            'contact_street': self.contact_street,
            'contact_phone': self.contact_phone,
            'contact_lon': self.contact_lon,
            'contact_lat': self.contact_lat,
            'contact_post_code': self.contact_post_code,
            'contact_fax': self.contact_fax
            })
        return d

    def as_dict(self):
        d = self.as_shallow()
        d.update({
            'entity': self.entity.as_shallow() if self.entity else None,
            'contact_country': self.contact_country.as_shallow() if self.contact_country else None,
            'main_category': self.main_category.as_shallow() if self.main_category else None,
            'sub_category': self.sub_category.as_shallow() if self.sub_category else None,
            'head': self.head.as_shallow() if self.head else None,
            'legal': self.legal.as_shallow() if self.legal else None,
            'financial_data': [fd.as_shallow(turnovers=True) for fd in self.financial_datas],
            'organisation_memberships': [om.as_dict(representative=False) for om in self.organisation_memberships],
            'accreditations': [a.as_dict(representative=False) for a in self.accreditations]
            })
        return d

    def __repr__(self):
        return "<Representative(%s,%r)>" % (self.id, self.entity)

Entity.representative = db.relationship(Representative,
        #primaryjoin=db.and_(Entity.id == Representative.entity_id,
        #                    Entity.serial == Representative.entity_serial),
        uselist=False,
        backref=db.backref('entity'))


