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

    def __repr__(self):
        return "<Country(%s)>" % (self.id)


