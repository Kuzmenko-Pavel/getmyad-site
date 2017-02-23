# encoding: utf-8
# Скрипт начисляет клики, не обработанные из-за ошибок.
# Обновляется коллекция stats_daily

from datetime import datetime

import pymongo

date_start = datetime(2011, 10, 13)
date_end = datetime(2011, 10, 14)
db = pymongo.Connection('yottos.com').getmyad_db

#db.stats_daily.update({'date': {'$gte': date_start, '$lte': date_end},
#                       'clicks': {'$exists': True, '$ne': 0}},
#                      {'$set': {'clicks': 0, 'cost': 0}})

i = 0
sum = 0
for click in db['clicks.error'].find({'dt': {'$gte': date_start, '$lte': date_end}}):
#    print click
    i += 1
    d = click['dt']
    dt = datetime(d.year, d.month, d.day)
    x = db.stats_daily.find_one({'date': dt, 'adv': click['inf'], 
                                 'totalCost': {'$gt': 0}})
    if not x:
        print i, '.', 
        continue
    delta = x['totalCost'] / x['clicksUnique']
    sum += delta
    if delta > 0.20:
        print "CUT OFF %s delta" % delta
        delta = 0.20
    x['totalCost'] += delta
    x['clicksUnique'] += 1
    print i, '_', x['totalCost'], '\t', delta, '\t', sum, 'payed off'
#    db.stats_daily.save(x)
