from itertools import groupby

from flask import Blueprint, request, redirect, url_for

from lobbyfacts.model.entity import Entity
from lobbyfacts.exc import NotFound, BadRequest
from lobbyfacts.util import jsonify, validate_cache
from lobbyfacts.util import response_format, stream_csv
from lobbyfacts.views.util import get_limit, get_offset, paged_url


def make_entity_api(cls):
    name = cls.__tablename__
    api = Blueprint(name, name)

    def filter_query():
        query = cls.all()
        try:
            filter_ = [f.split(':', 1) for f in request.args.getlist('filter')]
            for key, values in groupby(filter_, lambda a: a[0]):
                attr = getattr(cls, key)
                clause = db.or_(*[attr == v[1] for v in values])
                query = query.filter(clause)
            fts_query = request.args.get('q', '').strip()
            if len(fts_query) and hasattr(cls, 'entity'):
                query = query.join(Entity)
                query = query.filter('entity.full_text @@ plainto_tsquery(:ftsq)')
                query = query.order_by('ts_rank_cd(entity.full_text, plainto_tsquery(:ftsq)) DESC')
                query = query.params(ftsq=fts_query)
            return query
        except (ValueError, AttributeError, IndexError) as e:
            raise BadRequest(e)

    @api.route('/%s.<format>' % name)
    @api.route('/%s' % name)
    def index(format=None):
        q = filter_query()

        format = response_format(request)
        if format == 'csv':
            def generate():
                for entity in q:
                    if hasattr(entity, 'as_shallow'):
                        yield entity.as_shallow()
                    else:
                        yield entity.as_dict()
            return stream_csv(generate(), filename="%s.csv" % name)

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
