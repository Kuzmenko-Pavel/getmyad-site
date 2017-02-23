#!/usr/bin/python
# encoding: utf-8
import ConfigParser
import datetime

import os
import pymongo

PYLONS_CONFIG = "deploy.ini"
#PYLONS_CONFIG = "development.ini"

config_file = '%s./../%s' % (os.path.dirname(__file__), PYLONS_CONFIG)
print config_file
config = ConfigParser.ConfigParser()
config.read(config_file)

MONGO_HOST = config.get('app:main', 'mongo_host')
MONGO_USER = config.get('app:main', 'mongo_user')
MONGO_PASSWORD = config.get('app:main', 'mongo_password')
MONGO_DATABASE = config.get('app:main', 'mongo_database')


def _mongo_connection():
    ''' Возвращает Connection к серверу MongoDB '''
    try:
        connection = pymongo.Connection(host=MONGO_HOST)
    except pymongo.errors.AutoReconnect:
        # Пауза и повторная попытка подключиться
        from time import sleep
        sleep(1)
        connection = pymongo.Connection(host=MONGO_HOST)
    return connection

def _mongo_main_db():
    ''' Возвращает подключение к базе данных MongoDB '''
    return _mongo_connection()[MONGO_DATABASE]


if __name__ == '__main__':
    db = pymongo.Connection(host=MONGO_HOST).getmyad_db
    date = datetime.datetime.now()
    date = datetime.datetime(date.year, date.month, date.day, 0, 0)
    print date - datetime.timedelta(days=3)
    print date
    clicks = db.clicks.group(
            key = ['campaignTitle', 'campaignId',],
            condition = {'dt': {'$gte': date - datetime.timedelta(days=3),
                '$lt': date}, 'unique': True},
                reduce = '''function(obj,prev) { prev.count += 1; }''',
                initial = {'count': 0,})
    all = 0
    for item in clicks:
        all += item['count']
        print item['campaignTitle'].encode('utf-8'), " - ", item['count']

    print all
