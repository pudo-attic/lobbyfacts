from datetime import datetime

from lobbyfacts.core import db
from lobbyfacts.model.util import make_serial, make_id
from lobbyfacts.model.util import ReadJSONType, JSONEncoder

class AuditTrail(db.Model):
    __tablename__ = 'audit_trail'

    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'

    ACTIONS = [CREATE, UPDATE, DELETE]

    id = db.Column(db.String(36), primary_key=True, default=make_id)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    obj = db.Column(ReadJSONType)
    obj_id = db.Column(db.String(36))
    obj_type = db.Column(db.Unicode)
    action = db.Column(db.Unicode)

    @classmethod
    def create(cls, obj, action):
        trail = cls()
        assert action in cls.ACTIONS, action
        trail.action = action
        trail.obj = JSONEncoder().encode(obj.as_dict())
        trail.obj_id = obj.id
        trail.obj_type = obj.__tablename__
        trail.created_at = obj.updated_at
        db.session.add(trail)
        return trail

    def __repr__(self):
        return "<AuditTrail(%s,%s,%s)>" % (self.obj_type, self.obj_id, self.created_at)

    def as_dict(self):
        return {
                'id': self.id,
                'obj': self.obj,
                'created_at': self.created_at,
                'action': self.action
            }


class RevisionedMixIn(object):
    """ Simple versioning system for the database objects. We are
    creating an audit trail for each object so that we can 
    deserialize its history upon demand. """

    id = db.Column(db.String(36), primary_key=True, default=make_id)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)

    @classmethod
    def create(cls, data):
        """ Create a new, versioned object. """
        obj = cls()
        obj.id = make_id()
        obj.update(data)
        return obj

    def update(self, data):
        self.update_values(data)
        if not self in db.session:
            db.session.add(self)
        if db.session.is_modified(self, include_collections=False):
            self.updated_at = datetime.utcnow()
            action = AuditTrail.UPDATE if self.created_at else AuditTrail.CREATE
            AuditTrail.create(self, action)
        db.session.flush()
        return self

    def update_values(self, data):
        raise TypeError()

    def delete(self):
        pass

    def trail(self):
        q = db.session.query(AuditTrail)
        q = q.filter(AuditTrail.obj_id==self.id)
        q = q.filter(AuditTrail.obj_type==self.__tablename__)
        q = q.order_by(AuditTrail.created_at.desc())
        return q

    def as_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
            }

    @classmethod
    def by_attr(cls, attr, value):
        q = db.session.query(cls)
        q = q.filter(attr==value)
        return q.first()

    @classmethod
    def by_id(cls, id):
        q = db.session.query(cls)
        q = q.filter_by(id=id)
        return q.first()

    @classmethod
    def all(cls):
        q = db.session.query(cls)
        return q

