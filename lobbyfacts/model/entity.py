from lobbyfacts.core import db
from lobbyfacts.model.api import ApiEntityMixIn
from lobbyfacts.model.revision import RevisionedMixIn
from lobbyfacts.model.util import TSVector

class Entity(db.Model, RevisionedMixIn, ApiEntityMixIn):
    __tablename__ = 'entity'

    name = db.Column(db.Unicode)
    acronym = db.Column(db.Unicode)
    full_text = db.Column(TSVector)

    def update_values(self, data):
        self.name = data.get('name')
        self.acronym = data.get('acronym')

    def update_index(self):
        self.full_text = self.as_full_text()

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

    def as_full_text(self):
        text = [self.name, self.acronym]
        for obj in [self.person, self.organisation,
                self.representative]:
            if obj is None:
                continue
            for value in obj.as_shallow().values():
                text.append(unicode(value))
        text = [t for t in text if t is not None]
        return TSVector.make_text(db.engine, " ".join(text))

    def __repr__(self):
        return "<Entity(%s,%s)>" % (self.id, self.name.encode('ascii', 'ignore'))

