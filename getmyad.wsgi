# encoding: utf-8

import os, sys
project_dir = os.path.dirname( os.path.realpath( __file__ ) )
project_ini = os.path.join(project_dir, 'deploy.ini')
sys.path.append(project_dir)
from paste.deploy import loadapp
application = loadapp('config:%s' % project_ini)
from paste.script.util.logging_config import fileConfig
fileConfig(project_ini)
