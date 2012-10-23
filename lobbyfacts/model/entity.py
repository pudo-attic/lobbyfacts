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

    def as_shallow(self):
        d = super(Entity, self).as_dict()
        d['name'] = self.name
        d['uri'] = self.uri
        d['acronym'] = self.acronym
        return d

    def as_dict(self):
        d = self.as_shallow()
        d['person'] = self.person.as_shallow() if self.person else None
        d['organisation'] = self.organisation.as_shallow() if self.organisation else None
        d['representative'] = self.representative.as_shallow() if self.representative else None
        d['turnovers'] = [ft.as_dict(entity=False) for ft in self.turnovers]
        return d


    def __repr__(self):
        return "<Entity(%s,%s)>" % (self.id, self.name.encode('ascii', 'ignore'))

