from openinterests.core import db
from openinterests.model.revision import RevisionedMixIn


class Entity(db.Model, RevisionedMixIn):
    __tablename__ = 'entity'

    name = db.Column(db.Unicode)
    acronym = db.Column(db.Unicode)

    representative = db.relationship('Representative',
        primaryjoin=db.and_('Entity.id == Representative.entity_id',
                            'Representative.current == True'),
        uselist=False,
        backref=db.backref('entity'))

    def update_values(self, data):
        self.name = data.get('name')
        self.acronym = data.get('acronym')

    @classmethod
    def by_name(cls, name):
        return cls.by_attr(cls.name, name)

    def __repr__(self):
        return "<Entity(%s,%s)>" % (self.id, self.name.encode('ascii', 'ignore'))

