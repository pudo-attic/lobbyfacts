from openinterests.core import db
from openinterests.model.api import ApiEntityMixIn
from openinterests.model.revision import RevisionedMixIn


class Entity(db.Model, RevisionedMixIn, ApiEntityMixIn):
    __tablename__ = 'entity'

    name = db.Column(db.Unicode)
    acronym = db.Column(db.Unicode)


    def update_values(self, data):
        self.name = data.get('name')
        self.acronym = data.get('acronym')

    @classmethod
    def by_name(cls, name):
        return cls.by_attr(cls.name, name)

    def as_dict(self):
        d = super(Entity, self).as_dict()
        d['name'] = self.name
        d['uri'] = self.uri
        return d

    def __repr__(self):
        return "<Entity(%s,%s)>" % (self.id, self.name.encode('ascii', 'ignore'))

