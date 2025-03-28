# -*- coding: UTF-8 -*-
from __future__ import absolute_import

"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper


def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error', action="document")
    map.connect('/error/{action}/{id}', controller='error', action="document")

    # CUSTOM ROUTES HERE
    map.connect('/rpc', controller='rpc')
    map.connect('/adload', controller='adload', action="index")
    map.connect('/adload/', controller='adload', action="index")
    map.connect('/manager/checkInformers', controller='manager', action='checkInformers')

    map.connect('/', controller='main', action='index')
    map.connect('/{controller}/{action}')
    map.connect('/{controller}/{action}/{id}')
    # map.connect('*', controller='main', action='index')

    return map
