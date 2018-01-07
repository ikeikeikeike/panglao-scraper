import os

from plan import Plan

pjoin = os.path.join
dir_path = os.path.dirname(os.path.realpath(__file__))

# Django command
#
exchanger = Plan(
    'lifecycle',
    path=pjoin(dir_path, '../scraper'),
    environment={'DJANGO_SETTINGS_MODULE': 'scraper.settings_production'}
)

cmd = 'manage.py lifecycle >> /tmp/django_lifecycle.log 2>&1'
exchanger.script(cmd, every='1.days', at='minute.20')

if __name__ == "__main__":
    exchanger.run('update')
