
from fabric.api import *

env.hosts = ['norton.pudo.org']
deploy_dir = '/var/www/api.lobbyfacts.eu/'
backup_dir = '/var/www/opendatalabs.org/backup'
remote_user = 'fl'
pip_cmd = deploy_dir + 'bin/pip '

def deploy():
    run('mkdir -p ' + backup_dir)
    run('pg_dump -f ' + backup_dir + '/lobbyfacts_api-`date +%Y%m%d`.sql lobbyfacts_api')
    run('pg_dump -f ' + backup_dir + '/lobbyfacts_etl-`date +%Y%m%d`.sql lobbyfacts_etl')
    with cd(deploy_dir + 'src/lobbyfacts'):
        run('git pull')
        run('git reset --hard HEAD')
        run(pip_cmd + 'install -r requirements.txt')
    sudo('supervisorctl reread')
    sudo('supervisorctl restart lobbyfacts')
    run('curl -X PURGEDOMAIN http://api.lobbyfacts.eu')

def install():
    sudo('rm -rf ' + deploy_dir)
    sudo('mkdir -p ' + deploy_dir)
    sudo('chown -R ' + remote_user + ' ' + deploy_dir)
    put('deploy/*', deploy_dir)

    sudo('mv ' + deploy_dir + 'nginx.conf /etc/nginx/sites-available/api.lobbyfacts.eu')
    sudo('ln -sf /etc/nginx/sites-available/api.lobbyfacts.eu /etc/nginx/sites-enabled/api.lobbyfacts.eu')
    sudo('service nginx restart')

    sudo('ln -sf ' + deploy_dir + 'supervisor.conf /etc/supervisor/conf.d/api.lobbyfacts.eu.conf')
    run('mkdir ' + deploy_dir + 'logs')
    sudo('chown -R www-data.www-data ' + deploy_dir + 'logs')

    run('virtualenv ' + deploy_dir)
    run(pip_cmd + 'install gunicorn gevent')
    run(pip_cmd + 'install -e git+git@github.com:pudo/lobbyfacts.git#egg=lobbyfacts')

    deploy()

