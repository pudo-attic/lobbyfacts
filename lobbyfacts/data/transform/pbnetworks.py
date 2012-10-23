import logging
from hashlib import sha1
from itertools import count
from collections import defaultdict

import pbclient

from lobbyfacts.core import app as flask_app
from lobbyfacts.data import sl, etl_engine

QUORUM = 1

LIMIT = 500

log = logging.getLogger(__name__)

def _iterate(f, *a, **kwargs):
    kwargs['limit'] = LIMIT
    for i in count():
        kwargs['offset'] = LIMIT * i
        trs = f(*a, **kwargs)
        if not len(trs):
            break
        for taskrun in trs:
            yield taskrun

def setup():
    pbclient.set('endpoint', flask_app.config.get('ETL_PYBOSSA_HOST'))
    pbclient.set('api_key', flask_app.config.get('ETL_PYBOSSA_KEY'))
    apps = pbclient.find_app(short_name='openinterests-entitymarkup')
    return apps.pop()

def create_tasks(engine):
    log.info("Updating tasks on pyBossa...")
    app = setup()
    with flask_app.open_resource('resources/pbnetworks_template.html') as f:
        app.info['task_presenter'] = f.read()
        pbclient.update_app(app)
    tasks = pbclient.get_tasks(app.id, limit=30000)
    existing = dict([(t.data.get('info').get('signature'), t) for t in tasks])
    for rep in sl.all(engine, sl.get_table(engine, 'representative')):
        networking = rep.get('networking')
        if networking is None or len(networking.strip()) < 3:
            continue
        signature = rep.get('identification_code') + networking
        signature = sha1(signature.encode('ascii', 'ignore')).hexdigest()
        rep['signature'] = signature
        print [rep.get('name')]
        log.debug("Task: %s", rep['name'])
        rep['last_update_date'] = rep['last_update_date'].isoformat()
        rep['registration_date'] = rep['registration_date'].isoformat()
        #print [(k, type(v)) for k,v in rep.items()]
        if signature in existing:
            task = existing.get(signature)
            task.data['info'] = rep
            pbclient.update_task(task)
        else:
            pbclient.create_task(app.id, rep)

def flush_taskruns(engine):
    log.info("Flushing task results from pyBossa...")
    app = setup()
    for taskrun in _iterate(pbclient.find_taskruns, app_id=app.id):
        pbclient.delete_taskrun(taskrun)

def normcmp(a, b):
    return a.strip().lower() == b.strip().lower()

def fetch_taskruns(engine):
    log.info("Fetching responses from pyBossa...")
    net = sl.get_table(engine, 'network_entity')
    app = setup()
    results = defaultdict(list)
    for taskrun in _iterate(pbclient.find_taskruns, app_id=app.id):
        results[taskrun.info.get('etl_id')].extend(taskrun.info.get('matches'))
    for etl_id, matches in results.items():
        uniques = defaultdict(list)
        for m in matches: 
            uniques[m.strip().lower()].append(m)
        for vs in uniques.values():
            if not len(vs) >= QUORUM:
                continue
            sl.upsert(engine, net, {'etl_id': etl_id, 'name': vs[0].strip()},
                      ['etl_id', 'name'])

def transform(engine):
    #flush_taskruns(engine)
    fetch_taskruns(engine)
    create_tasks(engine)

if __name__ == '__main__':
    engine = etl_engine()
    transform(engine)




