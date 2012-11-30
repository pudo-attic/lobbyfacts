from itertools import groupby

from flask import Blueprint, request, redirect, url_for

from lobbyfacts.core import db
from lobbyfacts.model.entity import Entity
from lobbyfacts.exc import NotFound, BadRequest
from lobbyfacts.util import jsonify, validate_cache
from lobbyfacts.util import response_format, stream_csv
from lobbyfacts.views.util import get_limit, get_offset, paged_url


def make_entity_api(cls):
    name = cls.__tablename__
    mapper = cls.__mapper__
    api = Blueprint(name, name)

    def filter_query(query):
        query.has_fts = False
        filters = []
        try:
            filter_ = [f.split(':', 1) for f in request.args.getlist('filter')]
            for key, values in groupby(filter_, lambda a: a[0]):
                key = key if key in mapper.c else key + '_id'
                attr = getattr(cls, key)
                clause = db.or_(*[attr == v[1] for v in values])
                query = query.filter(clause)
            fts_query = request.args.get('q', '').strip()
            if len(fts_query) and hasattr(cls, 'entity'):
                query.has_fts = True
                query = query.join(Entity)
                query = query.filter('entity.full_text @@ plainto_tsquery(:ftsq)')
                query = query.params(ftsq=fts_query)
            return query
        except (ValueError, AttributeError, IndexError) as e:
            raise BadRequest(e)

    def make_facets():
        facets = {}
        try:
            for facet in request.args.getlist('facet'):
                count = db.func.count(cls.id)
                attr = getattr(cls, facet)
                if facet in mapper.c:
                    query = db.session.query(attr, count)
                    query = query.group_by(attr)
                else:
                    pcls = mapper.get_property(facet).mapper.class_
                    query = db.session.query(pcls, count)
                    query = query.join(attr)
                    query = query.group_by(pcls.id)
                query = filter_query(query)
                query = query.order_by(count.desc())
                facets[facet] = query
            return facets
        except (ValueError, AttributeError, IndexError) as e:
            raise BadRequest(e)

    @api.route('/%s.<format>' % name)
    @api.route('/%s' % name)
    def index(format=None):
        request.cache_key['args'] = request.args.items()
        q = filter_query(cls.all())

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
        if q.has_fts:
            q = q.order_by('ts_rank_cd(entity.full_text, plainto_tsquery(:ftsq)) DESC')
        limit = get_limit()
        q = q.limit(limit)
        offset = get_offset()
        q = q.offset(offset)
        return jsonify({
            'count': count,
            'next': paged_url('.index', limit, offset+limit) if count > offset else False, 
            'previous': paged_url('.index', limit, offset-limit) if offset > 0 else False,
            'limit': limit,
            'offset': offset,
            'results': q,
            'facets': make_facets()
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

    @api.route('/%s/<id>/trail' % name)
    def trail(id):
        obj = cls.by_id(id)
        if obj is None:
            return NotFound(id)

        return jsonify(obj.trail())

    return api
