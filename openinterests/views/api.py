from flask import Blueprint, request, redirect, url_for
from flask import render_template, flash

from openinterests.exc import NotFound
from openinterests.util import jsonify

def make_entity_api(cls):
    name = cls.__tablename__
    api = Blueprint(name, name)

    @api.route('/%s' % name)
    def index():
        q = cls.all()
        return jsonify({
            'count': q.count(),
            'results': q
            })

    @api.route('/%s/<id>' % name)
    def view(id):
        obj = cls.by_id(id)
        if obj is None:
            return NotFound(id)
        return jsonify(obj)

    return api
