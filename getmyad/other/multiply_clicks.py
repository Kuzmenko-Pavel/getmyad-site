# encoding: utf-8
''' 
Скрипт изменяет количество кликов у пользователя GetMyAd.

Имеет следующие особенности:

1. Работает только для текущего дня.
2. Изменение задаётся множителем.
3. Реально полученный CTR будет отличаться от заданного в большую сторону.
   Это связано с тем, что невозможно начислить дробное число кликов.
4. Скрипт отработает только в случае, если в день был хотя бы один клик.
5. Изменения, внесённые скриптом будут видны в аккаунтах после агрегации
   статистики (от 10 до 30 минут).

Формат использования::

    python [OPTIONS] multiply_clicks.py account k

``account``
    Аккаунт GetMyAd

``k``
    Коэффициент пересчёта кликов. Если больше 1, то клики будут добавляться,
    если меньше 1 -- убираться. Начисленная сумма также меняется
    пропорционально этому коэффициенту.

[OPTIONS] -- это следующие необязательные параметры:

``--host``
    Адрес сервера MongoDB. По умолчанию равно "localhost".

``--db``
    Наименование базы данных getmyad. По умолчанию "getmyad_db"

``--port``
    Порт MongoDB. По умолчанию равен 27017.

Пример использования::

    python multiply_clicks.py helpers.com.ua 1.5

Пользователю helpers.com.ua будет начислено приблизительно в полтора раза
больше кликов, чем имеется на данный момент.
'''

import datetime
import math
import optparse
import sys

import pymongo

if __name__ == '__main__':
    # Парсим аргументы командной строки
    usage = "usage: %prog account k"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--host', default="srv-3.yottos.com", help="MongoDB host")
    parser.add_option('--db', default="getmyad_db", help="database name")
    parser.add_option('--port', default=27018, type='int', help="MongoDB port")

    options, args = parser.parse_args()
    if len(args) != 2:
        parser.print_help()
        sys.exit(1)
    account = args[0]
    try:
        k = float(args[1])
    except ValueError:
        print u"Неправильный формат коэффициента. Пример: '1.5'"
        sys.exit(4)

    # Подключаемся к базе данных и получаем данные об информерах пользователя
    conn = pymongo.Connection(host=options.host, port=options.port)
    db = conn[options.db]
    if not db.users.find_one({'login': account}):
        print u"Пользователь %s не найден!" % account
        sys.exit(2)

    informers = db.informer.find({'user': account}, ['guid'])
    informers = [x['guid'] for x in informers]
    if not informers:
        print u"У пользователя %s нет ни одного информера"
        sys.exit(3)
    print informers

    # Обновляем клики
    d = datetime.datetime.today()
    today = datetime.datetime(d.year, d.month, d.day)
    print today
    diff_total = 0        # Разница в расчитанных и реальных кликах
    cursor = db.stats_daily.find({'date': today,
                                  #'adv': {'$in': informers},
                                  'adv': 'edab4030-ac9c-11e2-888a-00e081bad46b',
                                  'clicksUnique': {'$gt': 0}})
    cost = 0
    for x in cursor:
        clicks_old = x['clicksUnique']
        clicks = math.ceil(clicks_old * k)
        diff = clicks - clicks_old
        if diff == 0:
            continue
        diff_total += diff
        x['totalCost'] = round(x['totalCost'] * clicks / clicks_old, 2)
        cost += x['totalCost']
        x['clicksUnique'] = clicks
        if x['clicks'] < clicks:
            x['clicks'] = clicks
        #db.stats_daily.save(x)
        #print x['totalCost']
        #print clicks_old
        #print clicks
    print cost
    # Выводим разницу в кликах
    if diff_total > 0:
        print u"Добавлено %d кликов" % diff_total
    elif diff_total < 0:
        print u"Удалено %d кликов" % -diff_total
    else:
        print u"Ничего не изменилось"
        
    # Считаем полученный CTR
    impressions = clicks = 0
    for x in db.stats_daily.find({'date': today, 'adv': {'$in': informers}}):
        impressions += x.get('impressions', 0)
        clicks += x.get('clicksUnique', 0)
    try:
        ctr = clicks * 100.0 / impressions
    except ZeroDivisionError:
        ctr = 0.
    print u"Полученный CTR: %s %%" % round(ctr, 4)

