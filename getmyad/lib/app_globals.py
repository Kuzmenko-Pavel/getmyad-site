# -*- coding: UTF-8 -*-
from __future__ import absolute_import
"""The application's Globals object"""

import logging
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from pymongo import MongoClient
from pymongo.read_preferences import ReadPreference
from getmyad.lib import mongodb_proxy
import xmlrpclib
from pylons import config
import pymssql

log = logging.getLogger(__name__)


class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application

    """

    def __init__(self, config):
        """One instance of Globals is created during application
        initialization and is available during requests via the
        'app_globals' variable

        """
        self.config = config
        self.cache = CacheManager(**parse_cache_config_options(config))
        self.db = self.create_mongo_connection()
        self.db_m = self.create_master_mongo_connection()
        self.hidden_campaign = ['f3aa8177-b156-4788-a320-78278cf21ee7', 'a853b173-c168-40e1-9cb5-f1b0eec82b7e',
                                'e98c809f-be3f-4b71-af8e-c6e881848b06']

    def create_mongo_connection(self):
        ''' Подключается к монге, возвращает объект подключения '''
        c = mongodb_proxy.MongoProxy(MongoClient(host=self.config.get('mongo_host', 'localhost'),
                                                 replicaSet=self.config.get('mongo_replica_set', 'vsrv'),
                                                 read_preference=ReadPreference.SECONDARY_PREFERRED, connect=False), log)
        db = c[self.config.get('mongo_database', 'getmyad_db')]
        return db

    def create_master_mongo_connection(self):
        ''' Подключается к монге, возвращает объект подключения '''
        c = mongodb_proxy.MongoProxy(MongoClient(host=self.config.get('mongo_host', 'localhost'),
                                                 replicaSet=self.config.get('mongo_replica_set', 'vsrv'),
                                                 read_preference=ReadPreference.PRIMARY_PREFERRED, connect=False), log)
        db = c[self.config.get('mongo_database', 'getmyad_db')]
        return db

    @property
    def getmyad_rpc(self):
        ''' Возвращает объект ServerProxy для GetMyAd '''
        return xmlrpclib.ServerProxy(config['getmyad_xmlrpc_server'], use_datetime=True)

    @property
    def partner_account_enable(self):
        ''' Включон или выключен доступ для партнёрских аккаунтов '''
        return config.get('partner_account_enable',True) in ['True','true']

    @property
    def connection_adload(self):
        pymssql.set_max_connections(450)
        conn = pymssql.connect(host='srv-3.yottos.com',
                               user='web',
                               password='odif8duuisdofj',
                               database='AdLoad',
                               as_dict=True,
                               charset='cp1251')
        conn.autocommit(True)
        return conn
