from openinterests.core import db
from openinterests.model.revision import RevisionedMixIn
from openinterests.model.entity import Entity

class Representative(db.Model, RevisionedMixIn):
    __tablename__ = 'representative'

    entity_id = db.Column(db.String(36), db.ForeignKey('entity.id'))

    identitfication_code = db.Column(db.Unicode)

    goals = db.Column(db.Unicode)
    activities = db.Column(db.Unicode)
    status = db.Column(db.Unicode)
    networking = db.Column(db.Unicode)
    legal_status = db.Column(db.Unicode)
    code_of_conduct = db.Column(db.Unicode)
    web_site_url = db.Column(db.Unicode)

    members = db.Column(db.Integer, nullable=True)
    number_of_natural_persons = db.Column(db.Integer, nullable=True)
    number_of_organisations = db.Column(db.Integer, nullable=True)

    registration_date = db.Column(db.DateTime)
    last_update_date = db.Column(db.DateTime)

    contact_more = db.Column(db.Unicode)
    contact_town = db.Column(db.Unicode)
    contact_number = db.Column(db.Unicode)
    contact_street = db.Column(db.Unicode)
    contact_phone = db.Column(db.Unicode)
    contact_post_code = db.Column(db.Unicode)
    contact_fax = db.Column(db.Unicode)
    contact_country_id = db.Column(db.Integer, db.ForeignKey('country.id'))

    main_category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    sub_category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
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
        self.contact_country = data.get('contact_country')

        self.main_category = data.get('main_category')
        self.sub_category = data.get('sub_category')

        self.head_id = data.get('head').id
        self.legal_id = data.get('legal').id

    @classmethod
    def by_identification_code(cls, identitfication_code):
        return cls.by_attr(cls.identitfication_code,
                           identitfication_code)

    def __repr__(self):
        return "<Representative(%s,%r)>" % (self.id, self.entity)

Entity.representative = db.relationship(Representative,
        primaryjoin=db.and_(Entity.id == Representative.entity_id,
                            Entity.current == True),
        uselist=False,
        backref=db.backref('entity'))


