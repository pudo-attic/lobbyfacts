from flask import Blueprint, request, redirect, url_for
import inspect

from lobbyfacts.exc import NotFound
from lobbyfacts.model import REPORTS
from lobbyfacts.util import response_format, stream_csv
from lobbyfacts.util import jsonify, validate_cache
from lobbyfacts.views.util import get_limit, get_offset, paged_url

reports = Blueprint('reports', 'reports')

def get_results(q):
    results = q
    if len(q.column_descriptions) > 1:
        results = []
        headers = [cd['name'] for cd in q.column_descriptions]
        for result in q:
            results.append(dict(zip(headers, result)))
    return results

@reports.route('/reports')
def report_index():
    reports = []
    for name, report in REPORTS.items():
        argspec = inspect.getargspec(report)
        r = {
            'name': name,
            'description': report.__doc__,
            'params': argspec.args,
            'uri': url_for('.report', name=name, _external=True)
            }
        reports.append(r)
    return jsonify({'count': len(REPORTS), 'results': reports})

@reports.route('/reports/<name>.<format>')
@reports.route('/reports/<name>')
def report(name, format=None):
    if name not in REPORTS:
        return NotFound(name)
    func = REPORTS[name]
    argspec = inspect.getargspec(func)
    args = {}
    for k, v in request.args.items():
        if k in argspec.args:
            args[k] = v
    try:
        q = func(**args)
    except Exception, exc:
        return jsonify({'error': unicode(exc)}, status=400)
    
    format = response_format(request)
    if format == 'csv':
        return stream_csv(get_results(q), filename="%s.csv" % name)

    count = q.count()
    limit = get_limit()
    q = q.limit(limit)
    offset = get_offset()
    q = q.offset(offset)
    return jsonify({
        'count': count,
        'next': paged_url('.report', limit, offset+limit, name=name),
        'previous': paged_url('.report', limit, offset-limit, name=name),
        'limit': limit,
        'offset': offset,
        'query': str(q),
        'results': get_results(q)
        }, shallow=True)
