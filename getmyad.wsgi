# encoding: utf-8
# Скрипт для загрузки WSGI-приложения (Getmyad) и связи его с Apache
# Предполагается, что скрипт лежит в корне папки с проектом

import os, sys
project_dir = os.path.dirname( os.path.realpath( __file__ ) )
project_ini = os.path.join(project_dir, 'deploy.ini')

sys.path.append(project_dir)
os.environ['PYTHON_EGG_CACHE'] = '/usr/lib/python2.7/dist-packages'

from paste.deploy import loadapp
application = loadapp('config:%s' % project_ini)

from paste.script.util.logging_config import fileConfig
fileConfig(project_ini)
