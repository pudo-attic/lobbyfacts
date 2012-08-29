from datetime import datetime

from openinterests.core import db
from openinterests.model import util
from openinterests.model.api import ApiEntityMixIn

class Category(db.Model, ApiEntityMixIn):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'),
            nullable=True)
    name = db.Column(db.Unicode)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
            onupdate=datetime.utcnow)

    main_reps = db.relationship('Representative', 
            primaryjoin='Representative.main_category_id==Category.id',
            lazy='dynamic',
            backref='main_category')

    sub_reps = db.relationship('Representative', 
            primaryjoin='Representative.sub_category_id==Category.id',
            lazy='dynamic',
            backref='sub_category')

    children = db.relationship('Category',
            lazy='dynamic',
            backref=db.backref('parent', remote_side=[id]))

    @classmethod
    def create(cls, data):
        cls = cls()
        return cls.update(data)

    def update(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        if data.get('parent'):
            self.parent = data.get('parent')
        db.session.add(self)
        return self

    @classmethod
    def by_id(cls, id):
        q = db.session.query(cls)
        q = q.filter_by(id=id)
        return q.first()

    @classmethod
    def all(cls):
        return db.session.query(cls)


    def as_shallow(self):
        return {
            'uri': self.uri,
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
            }

    def as_dict(self):
        d = self.as_shallow()
        d.update({
            'parent': self.parent.as_shallow() if self.parent else None,
            'children': [c.as_shallow() for c in self.children]
            })
        return d

    def __repr__(self):
        return "<Category(%s)>" % (self.id)


