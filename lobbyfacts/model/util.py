import re
from uuid import uuid4
from time import time
from datetime import datetime
from json import dumps, loads
from sqlalchemy import sql
from sqlalchemy.types import Text, MutableType, TypeDecorator, \
    UserDefinedType


def make_id():
    return unicode(uuid4().hex)


def make_serial():
    return int(time() * 1000)


class TSVector(UserDefinedType):
    """Support for PostgreSQL full-text search."""

    def get_col_spec(self):
        from lobbyfacts.core import db
        if db.engine.dialect.name == 'postgresql':
            return 'tsvector'
        return 'text'

    @classmethod
    def make_text(cls, bind, text):
        if bind.engine.dialect.name == 'postgresql':
            return sql.select([sql.func.to_tsvector(text)], bind=bind).scalar()
        return text


class JSONType(MutableType, TypeDecorator):
    impl = Text

    def __init__(self):
        super(JSONType, self).__init__()

    def process_bind_param(self, value, dialect):
        return dumps(value)

    def process_result_value(self, value, dialiect):
        return loads(value)

    def copy_value(self, value):
        return loads(dumps(value))

