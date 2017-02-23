#!/usr/bin/python
# encoding: utf-8
import ConfigParser

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
    dbr = pymongo.Connection(host="srv-4.yottos.com").getmyad_db 
    clicks = dbr.stats_daily.rating.find({})
    print clicks.count()
    buffer = {}
    for x in clicks:
        key = (x['adv'],x['guid'],x['campaignTitle'],x['title'],x['campaignId'])
        buffer[key] = x.get('full_clicks',0)

    for key,value in buffer.items():
        db.stats_daily.rating.update({'adv': key[0],
                                      'guid': key[1],
                                      'campaignTitle': key[2],
                                      'title': key[3],
                                      'campaignId': key[4]},
                                      {'$set':{'full_clicks':value}},  upsert=False, w=0)

#        u = db.stats_daily.update({'guid': key[0],
#                               'title': key[1],
#                               'campaignId': key[2],
#                               'adv': key[3],
#                               'campaignTitle': key[4],
#                               'country': key[5],
#                               'city': key[6],
#                               'isOnClick': key[7],
#                               'date': key[8]},
#                               {'$set': {'clicks': value['cl'],
#                                         'view_seconds': value['vs'],
#                                         'clicksUnique': value['cl'],
#                                         'teaser_totalCost': value['cs'],
#                                         'totalCost': value['cs']}}, upsert=False, safe=True)
#
#        db.stats_daily.rating.update({'adv': key[3],
#                                      'guid': key[0],
#                                      'campaignTitle': key[4],
#                                      'title': key[1],
#                                      'campaignId': key[2]},
#                                      {'$set':{'clicks': value['cl'], 'full_clicks':value['cl']}},  upsert=False, w=0)
#        print u
