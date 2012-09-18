import logging
from hashlib import sha1

import pbclient

from openinterests.core import app as flask_app
from openinterests.data import sl, etl_engine


log = logging.getLogger(__name__)

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
    return 
    tasks = pbclient.get_tasks(app.id, limit=10000)
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

if __name__ == '__main__':
    engine = etl_engine()
    create_tasks(engine)





