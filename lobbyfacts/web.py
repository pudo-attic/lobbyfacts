from flask import Response, request, render_template
from hashlib import sha1

from lobbyfacts.core import app
from lobbyfacts.exc import NotFound
from lobbyfacts.util import NotModified, response_format
from lobbyfacts.util import validate_cache, jsonify
from lobbyfacts.views import *

@app.after_request
def configure_caching(response_class):
    if not app.config.get('CACHE'):
        return response_class
    if request.method in ['GET', 'HEAD', 'OPTIONS'] \
        and response_class.status_code < 400:
        try:
            etag, mod_time = validate_cache(request)
            response_class.add_etag(etag)
            response_class.cache_control.max_age = 84600 * 1
            response_class.cache_control.public = True
            if mod_time:
                response_class.last_modified = mod_time
        except NotModified:
            return Response(status=304)
    return response_class


@app.before_request
def setup_cache():
    args = request.args.items()
    args = filter(lambda (k,v): k != '_', args) # haha jquery where is your god now?!?
    query = sha1(repr(sorted(args))).hexdigest()
    request.cache_key = {'query': query}


@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(410)
@app.errorhandler(500)
def handle_exceptions(exc):
    """ Re-format exceptions to JSON if accept requires that. """
    format = response_format(request)
    if format == 'json':
        body = {'status': exc.code,
                'name': exc.name,
                'description': exc.get_description(request.environ)}
        return jsonify(body, status=exc.code,
                       headers=exc.get_headers(request.environ))
    return exc


@app.errorhandler(NotModified)
def handle_not_modified(exc):
    return Response(status=304)


@app.route('/')
def index():
    return render_template('index.tmpl')

@app.route('/reports/<report>')
def companies_by_exp(report):
    if report in ['companies_by_exp', 'tradeassoc_by_exp',
        'consultancies_by_turnover', 'lawfirms_by_turnover']:
        return render_template('reports/%s.tmpl' % report)
    raise NotFound()


if __name__ == "__main__":
    app.run(port=5002)
