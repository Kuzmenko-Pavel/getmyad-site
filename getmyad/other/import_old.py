#!/usr/bin/python
# This Python file uses the following encoding: utf-8
import datetime

from pymongo import Connection, DESCENDING
import pymongo
import bson.objectid




# Сервер основной базы данных, куда будет помещена обработанная статистика
main_db_host = 'yottos.ru,213.186.121.76:27018,213.186.121.199:27018'

# Адрес базы данных mongo, в которые пишет свои данные getmyad-worker
getmyad_worker_mongo_host = 'localhost'


conn = Connection(host=main_db_host)
db = conn.getmyad_db

def importImpressionsFromMongo(log_db_host):
    """ Импортирует статистику о показах из журнальной базы данных log_db_host/getmyad
        (для новой версии getmyad-worker)
        
        Возвращает структуру вида::
        
            {
                count:        (кол-во обработанных записей),
                elapsed_time: (затраченное время, в секундах)
            }
        
         """
    elapsed_start_time = datetime.datetime.now()
    global db                   # База данных со статистикой
    mongo = Connection(log_db_host)
    db2 = mongo.getmyad         # База данных с журналом показов
    
    # _id последней записи, обработанной скриптом. Если не было обработано ничего, равно None 
    last_processed_id = None          
    try:
        last_processed_id = db2.config.find_one({'key': 'impressions last _id (2)'})['value']
    except:
        last_processed_id = None
    if not isinstance(last_processed_id, bson.objectid.ObjectId):
        last_processed_id = None

    cursor = db2['log.impressions'].find({}, {'keywords': False}).sort("$natural", DESCENDING)
    #cursor = db2['log.impressions'].find({}).sort("$natural", DESCENDING)
    try:
        end_id = cursor[0]['_id']   # Последний id, который будет обработан в этот раз
        print end_id
    except:
        print "importImpressionsFromMongo: nothing to do"
        return
    
    buffer = {}
    social_buffer = {}
    banner_buffer = {}
    banner_social_buffer = {}
    banner_buffer_stat = {}
    banner_social_buffer_stat = {}
    worker_stats = {}
    processed_records = 0
    processed_social_records = 0
    processed_paymend_records = 0
    banner_processed_social_records = 0
    banner_processed_paymend_records = 0
    try:
        for x in cursor:
            if last_processed_id <> None and x['_id'] == last_processed_id:
                break
            n = x['dt']
            dt = datetime.datetime(n.year, n.month, n.day)
            if x.get('project', 'adload') == 'adload':
                if x.get('type', 'teaser' ) == 'banner' :
                    print "banner in ADLOAD ??? CRAZY"
                else:
                    if x.get('social', False):
                        key = (x['id'], x['title'], x['inf'].lower(), dt, x['campaignId'].lower(), x['campaignTitle'], x['country'],\
                                x['region'], x.get('isOnClick', True))
                        social_buffer[key] = social_buffer.get(key, 0) + 1
                        processed_social_records +=1
                        processed_records += 1
                    else:
                        key = (x['id'], x['title'], x['inf'].lower(), dt, x['campaignId'].lower(), x['campaignTitle'], x['country'],\
                                x['region'], x.get('isOnClick', True))
                        buffer[key] = buffer.get(key, 0) + 1
                        processed_paymend_records +=1
                        processed_records += 1
            elif x.get('project', 'adload') == 'banner':
                if x.get('type', 'teaser' ) == 'teaser' :
                    print "teaser in BANNER ??? CRAZY"
                else:
                    if x.get('social', False):
                        key = (x['id'], x['title'], x['inf'].lower(), dt, x['campaignId'].lower(), x['campaignTitle'], x['country'],\
                                x['region'], x.get('isOnClick', True))
                        key_stat = (x['id'], x['title'], x['inf'].lower(), dt, x['campaignId'].lower(), x['campaignTitle'])
                        banner_social_buffer[key] = banner_social_buffer.get(key, 0) + 1
                        banner_social_buffer_stat[key_stat] = banner_social_buffer_stat.get(key_stat, 0) + 1
                        banner_processed_social_records +=1
                        processed_records += 1
                    else:
                        key = (x['id'], x['title'], x['inf'].lower(), dt, x['campaignId'].lower(), x['campaignTitle'], x['country'],\
                                x['region'], x.get('isOnClick', True))
                        key_stat = (x['id'], x['title'], x['inf'].lower(), dt, x['campaignId'].lower(), x['campaignTitle'])
                        banner_buffer[key] = banner_buffer.get(key, 0) + 1
                        banner_buffer_stat[key_stat] = banner_buffer_stat.get(key_stat, 0) + 1
                        banner_processed_paymend_records +=1
                        processed_records += 1
            elif x.get('project', 'adload') == 'cleverad':
                print "CleverAd"
            else:
                print "HZ"
            stats_key = (x.get('branch', 'NOT'), dt, x.get('conformity', 'NOT'))
            stats_key_all = (x.get('branch', 'NOT'), dt, 'ALL')
            worker_stats[stats_key] = worker_stats.get(stats_key, 0) + 1
            worker_stats[stats_key_all] = worker_stats.get(stats_key_all, 0) + 1
    except Exception as e:
        print e
        pass
        

    db.reset_error_history()

    for key,value in buffer.items():
        db.stats_daily.update({'guid': key[0],
                               'title': key[1],
                               'campaignId': key[4],
                               'campaignTitle': key[5],
                               'adv': key[2],
                               'country': key[6],
                               'city': key[7],
                               'isOnClick': key[8],
                               'date': key[3]},
                               {'$inc': {'impressions': value}},
                               True)
        db.offer.update({'guid': key[0]},
                {'$inc': {'impressions': value, 'full_impressions': value}}, False)
        db.stats_daily.rating.update({'adv': key[2],
                                      'guid': key[0],
                                      'campaignId': key[4],
                                      'campaignTitle': key[5],
                                      'title': key[1]},
                                      {'$inc': {'impressions': value, 'full_impressions': value}},
                                      True)
    for key,value in social_buffer.items():
        db.stats_daily.update({'guid': key[0],
                               'title': key[1],
                               'campaignId': key[4],
                               'campaignTitle': key[5],
                               'adv': key[2],
                               'country': key[6],
                               'city': key[7],
                               'isOnClick': key[8],
                               'date': key[3]},
                               {'$inc': {'social_impressions': value}},
                               True)
        db.offer.update({'guid': key[0]},
                {'$inc': {'impressions': value, 'full_impressions': value}}, False)
        db.stats_daily.rating.update({'adv': key[2],
                                      'guid': key[0],
                                      'campaignId': key[4],
                                      'campaignTitle': key[5],
                                      'title': key[1]},
                                      {'$inc': {'impressions': value, 'full_impressions': value}},
                                      True)
    for key,value in banner_buffer.items():
        db.stats_daily.update({'guid': key[0],
                               'title': key[1],
                               'campaignId': key[4],
                               'campaignTitle': key[5],
                               'adv': key[2],
                               'country': key[6],
                               'city': key[7],
                               'isOnClick': key[8],
                               'date': key[3]},
                               {'$inc': {'banner_impressions': value}},
                               True)
        db.offer.update({'guid': key[0]},
                {'$inc': {'impressions': value, 'full_impressions': value}}, False)
        db.stats_daily.rating.update({'adv': key[2],
                                      'guid': key[0],
                                      'campaignId': key[4],
                                      'campaignTitle': key[5],
                                      'title': key[1]},
                                      {'$inc': {'impressions': value, 'full_impressions': value}},
                                      True)
    for key,value in banner_social_buffer.items():
        db.stats_daily.update({'guid': key[0],
                               'title': key[1],
                               'campaignId': key[4],
                               'campaignTitle': key[5],
                               'adv': key[2],
                               'country': key[6],
                               'city': key[7],
                               'isOnClick': key[8],
                               'date': key[3]},
                               {'$inc': {'banner_social_impressions': value}},
                               True)
        db.offer.update({'guid': key[0]},
                {'$inc': {'impressions': value, 'full_impressions': value}}, False)
        db.stats_daily.rating.update({'adv': key[2],
                                      'guid': key[0],
                                      'campaignId': key[4],
                                      'campaignTitle': key[5],
                                      'title': key[1]},
                                      {'$inc': {'impressions': value, 'full_impressions': value}},
                                      True)
    for key,value in banner_buffer_stat.items():
        db.banner.stats_daily.update({'guid': key[0],
                               'title': key[1],
                               'campaignId': key[4],
                               'campaignTitle': key[5],
                               'adv': key[2],
                               'date': key[3]},
                               {'$inc': {'banner_impressions': value}},
                               True)
    for key,value in banner_social_buffer_stat.items():
        db.banner.stats_daily.update({'guid': key[0],
                               'title': key[1],
                               'campaignId': key[4],
                               'campaignTitle': key[5],
                               'adv': key[2],
                               'date': key[3]},
                               {'$inc': {'banner_social_impressions': value}},
                               True)
    for key,value in worker_stats.items():
        db.worker_stats.update({'date': key[1]},
                {'$inc': {(str(key[0]) + '.' + str(key[2])): value}}, True)
    elapsed = (datetime.datetime.now() - elapsed_start_time).seconds
    print 'Tiser buffer has %s keys, %s tiser social keys, banner buffer has %s keys, %s banner social keys collected \
in %s seconds, %s records processed. \nFrom this tiser %s social records, tiser %s paymend record, \
banner %s social records, banner %s paymend record,' % \
            (len(buffer), len(social_buffer), len(banner_buffer), len(banner_social_buffer), elapsed, processed_records,\
            processed_social_records, processed_paymend_records, banner_processed_social_records, banner_processed_paymend_records)
    if db.previous_error():
        print "Database error", db.previous_error() 
    db2.config.update({'key': 'impressions last _id (2)'}, {'$set': {'value': end_id}}, True)
    return {'count': processed_records,
            'elapsed_time': (datetime.datetime.now() - elapsed_start_time).seconds}


if __name__ == '__main__':
    print datetime.datetime.now()
    result_imps = importImpressionsFromMongo(getmyad_worker_mongo_host)
    # Делаем запись об обработке статистики
    mongo = pymongo.Connection(host=main_db_host)['getmyad_db']
    if 'log.statisticProcess' not in mongo.collection_names():
        mongo.create_collection('log.statisticProcess',
                                capped=True, size=50000000, max=10000)
    mongo.log.statisticProcess.insert({'dt': datetime.datetime.now(),
                                       'impressions': result_imps,
                                       'clicks': 'not processed',
                                       'srv': '3'},   
                                       safe=True)
