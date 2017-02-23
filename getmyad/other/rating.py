#!/usr/bin/python
# This Python file uses the following encoding: utf-8
import xmlrpclib

from pymongo import Connection


# Сервер основной базы данных, куда будет помещена обработанная статистика
main_db_host = '213.186.119.106:27017,213.186.121.201:27018,213.186.121.84:27018'

conn = Connection(host=main_db_host)
db = conn.getmyad_db

ADLOAD_XMLRPC_HOST = 'http://adload.vsrv-1.2.yottos.com/rpc'


def rating_counting():
    adload = xmlrpclib.ServerProxy(ADLOAD_XMLRPC_HOST)
    border_impressions = 200
    offers = db.offer.find()
    offer_count = 0
    for offer in offers:
        impressions = offer.get('impressions', 0)
        clicks = offer.get('clicks', 0)

        if impressions > border_impressions:
            offer_count += 1
            offer_cost = adload.clickCost(offer['guid'])
            rating = ((float(clicks)/impressions) * 10000000) * offer_cost.get('cost', 1.5)
            db.offer.update({'guid': offer['guid']},{'$set': {'rating': round(rating, 4), 'impressions': 0, 'clicks': 0}}, False)

    print "Created %d rating for offer" % offer_count

if __name__ == '__main__':
    print "Rating"
    rating_counting()
