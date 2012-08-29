from flask import Blueprint, request, redirect, url_for
from flask import render_template, flash

from openinterests.exc import NotFound
from openinterests.util import jsonify, validate_cache

def arg_int(name, default=None):
    try:
        v = request.args.get(name)
        return int(v)
    except (ValueError, TypeError):
        return default

def get_limit(default=50):
    return max(0, min(500, arg_int('limit', default=default)))

def get_offset(default=0):
    return max(0, arg_int('offset', default=default))

def make_entity_api(cls):
    name = cls.__tablename__
    api = Blueprint(name, name)

    def paged_url(r, limit, offset):
        if offset < 0:
            return None
        args = request.args.items()
        args = [(k,v) for (k,v) in args if k not in ('limit', 'offset')]
        args.extend([('limit', limit), ('offset', offset)])
        return url_for(r, _external=True, **dict(args))

    @api.route('/%s' % name)
    def index():
        q = cls.all()
        count = q.count()
        limit = get_limit()
        q = q.limit(limit)
        offset = get_offset()
        q = q.offset(offset)
        return jsonify({
            'count': count,
            'next': paged_url('.index', limit, offset+limit),
            'previous': paged_url('.index', limit, offset-limit),
            'limit': limit,
            'offset': offset,
            'results': q
            }, shallow=True)

    @api.route('/%s/<id>' % name)
    def view(id):
        obj = cls.by_id(id)
        if obj is None:
            return NotFound(id)

        # check this before lazy-loading during serialization
        for v in ['updated_at', 'created_at']:
            if hasattr(obj, v):
                request.cache_key['modified'] = getattr(obj, v)
        validate_cache(request)

        return jsonify(obj)

    return api
