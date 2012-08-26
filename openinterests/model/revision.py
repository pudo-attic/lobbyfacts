from datetime import datetime

from openinterests.core import db
from openinterests.model.util import make_serial, make_id

class RevisionedMixIn(object):
    """ Simple versioning system for the database graph objects.
    This is based upon multiple objects sharing the smae ID, but
    differing in their serial number. Additionally, a ``current``
    flag is used to flag that revision of a given edge or node
    that should currently be used. """

    id = db.Column(db.String(36), primary_key=True, default=make_id)
    serial = db.Column(db.BigInteger, primary_key=True, default=make_serial)
    current = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, data):
        """ Create a new, versioned object. """
        obj = cls()
        obj.id = make_id()
        obj._update(None, data)
        return obj

    def update(self, data, current=True):
        """ Create a new object as a child of an existing,
        versioned object while changing the serial number to
        differentiate the child. """
        obj = self.__class__()
        obj.id = self.id
        return obj._update(self, data)

    def _changed(self, other):
        if other is None:
            return True
        for prop in self.__mapper__.iterate_properties:
            if prop.key in ['current', 'serial', 'created_at']:
                continue
            if getattr(self, prop.key) != getattr(other, prop.key):
                return True
        return False

    def _update(self, orig, data, current=True):
        self.update_values(data)
        if not self._changed(orig):
            return
        self.serial = make_serial()
        self.current = current
        if current and self.id:
            # this is slightly hacky but it cannot
            # be assumed that the `current` version
            # is the parent object to the new obj.
            table = self.__table__
            q = table.update().where(table.c.id == self.id)
            q = q.values({'current': False})
            db.session.execute(q)
        db.session.add(self)
        db.session.flush()
        return self

    def update_values(self, data):
        raise TypeError()

    def delete(self):
        table = self.__table__
        q = table.update().where(table.c.id == self.id)
        q = q.values({'current': False})
        db.session.execute(q)

    def as_dict(self):
        return {
            'id': self.id,
            'serial': self.serial,
            'current': self.current,
            'created_at': self.created_at
            }

    @property
    def history(self):
        q = db.session.query(self.__class__)
        q = q.filter_by(id=self.id)
        q = q.order_by(self.__class__.created_at.asc())
        return q

    @classmethod
    def by_attr(cls, attr, value):
        q = db.session.query(cls)
        q = q.filter_by(current=True)
        q = q.filter(attr==value)
        return q.first()

    @classmethod
    def by_id(cls, id):
        q = db.session.query(cls)
        q = q.filter_by(current=True)
        q = q.filter_by(id=id)
        return q.first()

    @classmethod
    def all(cls):
        q = db.session.query(cls)
        q = q.filter_by(current=True)
        return q
