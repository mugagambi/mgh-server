import random

from decouple import config
from fabric.api import cd, env, run, local, sudo
from fabric.contrib.files import exists, append

REPO_URL = 'git@github.com:mugagambi/mgh-server.git'


def live_deploy():
    site_folder = f'/home/{env.user}/mgh-server'
    run(f'mkdir  -p {site_folder}')
    with cd(site_folder):
        _get_latest_source()
        _update_virtualenv()
        # _create_or_update_dotenv_live()
        _update_static_files()
        _update_database()
        _create_main_server_folders()
        _create_main_webserver_files()
        _restart_live_server()


def _get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git init')
        run(f'git remote add origin {REPO_URL}')
        run('git fetch')
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run(f'git reset --hard {current_commit}')


def _update_virtualenv():
    if not exists('venv/bin/pip'):
        run(f'python3.6 -m venv venv')
    run('./venv/bin/pip install --upgrade pip')
    run('./venv/bin/pip install -r requirements.txt')


def _create_or_update_dotenv_live():
    run('rm .env')
    append('.env', f'DEBUG =false')
    append('.env',
           f'ALLOWED_HOSTS=www.mgh.nanoafrika.com')
    append('.env', f'DATABASE_URL={config("DATABASE_URL_LIVE")}')
    append('.env', f'EMAIL_BACKEND = django.core.mail.backends.smtp.EmailBackend')
    append('.env', f'BACKUP_PATH = /home/nanoafrika')
    append('.env', f'EMAIL_HOST = {config("EMAIL_HOST")}')
    append('.env', f'EMAIL_HOST_USER = {config("EMAIL_HOST_USER")}')
    append('.env', f'EMAIL_HOST_PASSWORD = {config("EMAIL_HOST_PASSWORD")}')
    append('.env', f'AWS_ACCESS_KEY_ID = {config("AWS_ACCESS_KEY_ID")}')
    append('.env', f'AWS_SECRET_ACCESS_KEY = {config("AWS_SECRET_ACCESS_KEY")}')
    append('.env', f'APP_NAME = mgh')
    append('.env',
           f'SENTRY = {config("SENTRY")}')
    current_contents = run('cat .env')
    if 'SECRET_KEY' not in current_contents:
        new_secret = ''.join(random.SystemRandom().choices('abcdefghijklmnopqrstuvwxyz0123456789', k=50))
        append('.env', f'SECRET_KEY={new_secret}')


def _update_static_files():
    run('./venv/bin/python manage.py collectstatic --noinput')


def _update_database():
    run('./venv/bin/python manage.py migrate --noinput')

def _create_main_server_folders():
    run(f'mkdir  -p /home/nanoafrika/run/')
    run(f'mkdir  -p /home/nanoafrika/logs')


def _create_main_webserver_files():
    if not exists('/home/nanoafrika/mgh_supervisior'):
        run('cp deploy_tools/mgh_supervisior /home/nanoafrika/')
        run('chmod u+x /home/nanoafrika/mgh_supervisior')
        run('touch /home/nanoafrika/logs/mgh.log')
        run('touch /home/nanoafrika/logs/nginx-access.log')
        run('touch /home/nanoafrika/logs/nginx-error.log')
        sudo('cp deploy_tools/mgh.conf /etc/supervisor/conf.d/')
        sudo('sudo supervisorctl reread')
        sudo('sudo supervisorctl update')
        sudo('sudo supervisorctl status mgh')
        sudo('cp deploy_tools/nginx.template.conf /etc/nginx/sites-available/mgh')
        sudo('ln -s /etc/nginx/sites-available/mgh /etc/nginx/sites-enabled/mgh')
        sudo('service nginx restart')

def _restart_live_server():
    sudo('rm -rf /tmp/*')
    sudo('supervisorctl restart mgh')


# Demo server config

def demo_deploy():
    site_folder = f'/home/{env.user}/agrisales-demo'
    run(f'mkdir  -p {site_folder}')
    with cd(site_folder):
        _demo_get_latest_source()
        _demo_update_virtualenv()
        # _demo_create_or_update_dotenv_live()
        _demo_update_static_files()
        _demo_update_database()
        _demo_seed_database()
        _restart_demo_server()


def _demo_get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git init')
        run(f'git remote add origin {REPO_URL}')
        run('git fetch')
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run(f'git reset --hard {current_commit}')


def _demo_update_virtualenv():
    if not exists('venv/bin/pip'):
        run(f'python3.6 -m venv venv')
    run('./venv/bin/pip install --upgrade pip')
    run('./venv/bin/pip install -r requirements.txt')


def _demo_create_or_update_dotenv_live():
    run('rm .env')
    append('.env', f'DEBUG =false')
    append('.env',
           f'ALLOWED_HOSTS=demo.agrisales.nanoafrika.com')
    append('.env', f'DEMO_DATABASE_URL={config("DEMO_DATABASE_URL_LIVE")}')
    append('.env', f'EMAIL_BACKEND = django.core.mail.backends.smtp.EmailBackend')
    append('.env', f'EMAIL_HOST = {config("EMAIL_HOST")}')
    append('.env', f'EMAIL_HOST_USER = {config("EMAIL_HOST_USER")}')
    append('.env', f'EMAIL_HOST_PASSWORD = {config("EMAIL_HOST_PASSWORD")}')
    append('.env', f'APP_NAME = demo')
    append('.env',
           f'SENTRY = {config("SENTRY")}')
    current_contents = run('cat .env')
    if 'SECRET_KEY' not in current_contents:
        new_secret = ''.join(random.SystemRandom().choices('abcdefghijklmnopqrstuvwxyz0123456789', k=50))
        append('.env', f'SECRET_KEY={new_secret}')


def _demo_update_static_files():
    run('./venv/bin/python manage.py collectstatic --noinput')


def _demo_update_database():
    run('./venv/bin/python manage.py migrate --noinput')


def _demo_seed_database():
    pass


def _restart_demo_server():
    sudo('systemctl restart demo.agrisales.nanoafrika.com')
