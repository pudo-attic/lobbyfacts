from flask import Blueprint, request, redirect, url_for

def arg_int(name, default=None):
    try:
        v = request.args.get(name)
        return int(v)
    except (ValueError, TypeError):
        return default

def get_limit(default=50):
    return max(0, min(50000, arg_int('limit', default=default)))

def get_offset(default=0):
    return max(0, arg_int('offset', default=default))

def paged_url(r, limit, offset, **kw):
    if offset < 0:
        return None
    args = request.args.items()
    args = [(k,v) for (k,v) in args if k not in ('limit', 'offset')]
    args.extend([('limit', limit), ('offset', offset)])
    args.extend(kw.items())
    return url_for(r, _external=True, **dict(args))

