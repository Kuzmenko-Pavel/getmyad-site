# encoding: utf-8
import ConfigParser
import datetime
import xmlrpclib

import os
import pymongo

PYLONS_CONFIG = "deploy.ini"
#PYLONS_CONFIG = "development.ini"

config_file = '%s../../%s' % (os.path.dirname(__file__), PYLONS_CONFIG)
print config_file
config = ConfigParser.ConfigParser()
config.read(config_file)

ADLOAD_XMLRPC_HOST = config.get('app:main', 'adload_xmlrpc_server')
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

def process_click(url, ip, click_datetime, offer_id, informer_id, token, server, city, country, campaignId):
    ''' Обработка клика пользователя по рекламному предложению.

        Задача ставится в очередь скриптом redirect.py или выполняется
        немедленно при недоступности Celery.

        В процессе обработки:

        1. IP ищется в чёрном списке.

        2. Проверяется, что по ссылке переходит тот же ip, которому она была
           выдана.

        3. Проверяется, что ссылка ещё не устарела.

        4. Если ip сделал больше трёх переходов за сутки, ip заносится в чёрный
           список.

        5. Клик передаётся в AdLoad.

        6. Только если все предыдущие пункты отработали нормально, клик
           записывается в GetMyAd. В противном случае, делается запись либо
           в ``clicks.rejected`` (отклонённые клики), либо в ``clicks.error``
           (клики, во время обработки которых произошла ошибка).

        ERROR ID LIST
        1 - Несовпадает Токен и IP
        2 - Найден в Чёрном списке IP
        3 - Более 3 переходов с РБ за сутки
        4 - Более 10 переходов с РБ за неделю
        5 - Более 5 переходов с ПС за сутки
        6 - Более 10 переходов с ПС за неделю
    '''
    print "/----------------------------------------------------------------------/"
    print "process click %s \t %s" % (ip, click_datetime)
    db = _mongo_main_db()
    title = ""
    
    def log_error(reason, campaign_id=None):
        print "error: ", reason 
#        db.clicks.error.insert({'ip': ip, 'offer': offer_id, 'dt': click_datetime,
#                                'title': title, 'token': token, 'server': server,
#                                'inf': informer_id, 'url': url, 'reason': reason,
#                                'campaignId': campaign_id},
#                                safe=True)
    def log_reject(reason, campaign_id=None):
        print 'reject:', reason
#        db.clicks.rejected.insert({'ip': ip, 'offer': offer_id, 'dt': click_datetime,
#                                   'title': title,  'token': token, 'server': server,
#                                   'inf': informer_id, 'url': url, 'reason': reason,
#                                   'campaignId': campaign_id},
#                                   safe=True)

    def _partner_click_cost(informer_id, adload_cost):
        ''' Возвращает цену клика для сайта-партнёра.
            
            ``informer_id``
                ID информера, по которому произошёл клик.

            ``adload_cost``
                Цена клика для рекламодателя. Используется в случае плавающей
                цены.
        '''
        try:
            user = db.informer.find_one({'guid': informer_id}, ['user'])['user']
            cursor = db.click_cost.find({'user.login': user,
                                         'date': {'$lte': click_datetime}}) \
                                  .sort('date', pymongo.DESCENDING) \
                                  .limit(1)
            x = cursor[0]
            payment_type = x.get('type', 'fixed') 
            if payment_type == 'floating':
                # Плавающая цена за клик
                percent = x['percent']
                cost_min = x.get('min')
                cost_max = x.get('max')
                cost = round(adload_cost * percent / 100, 2)
                if cost_min and cost < cost_min:
                    cost = cost_min
                if cost_max and cost > cost_max:
                    cost = cost_max
            else:
                # Фиксированная цена за клик
                payment_type = 'fixed'
                cost = float(x['cost'])
        except:
            cost = 0
        return cost
    

    # С тестовыми кликами ничего не делаем
    if token == "test":
        print "Processed test click from ip %s" % ip
        return
    
    # Ищём IP в чёрном списке
    if db.blacklist.ip.find_one({'ip': ip}):
        print "Blacklisted ip:", ip
        log_reject("Blacklisted ip")
        return
    
    social = db.campaign.find_one({'guid': campaignId}).get('social')
    
    if social:
        print "social" 
    
    # Определяем кампанию, к которой относится предложение
    try:
        campaign = db.offer.find_one({'guid': offer_id}, {'campaignId': True, 'campaignTitle': True, '_id': False})
        campaign_id = campaign['campaignId']
        campaign_title = campaign['campaignTitle']
    except (TypeError, KeyError):
        campaign_id = None
        campaign_title = None

    print "Campaign Title = %s " % campaign_title
    print "CampaignId = %s" % campaign_id

    # Ищем, не было ли кликов по этому товару
    # Заодно проверяем ограничение на MAX_CLICKS_FOR_ONE_DAY переходов в сутки
    # (защита от накруток)
    MAX_CLICKS_FOR_ONE_DAY = 3
    MAX_CLICKS_FOR_ONE_DAY_ALL = 5
    MAX_CLICKS_FOR_ONE_WEEK = 10
    MAX_CLICKS_FOR_ONE_WEEK_ALL = 10
    unique = True
    #Проверяе по рекламному блоку за день и неделю
    today_clicks = 0
    toweek_clicks = 0
    for click in db.clicks.find({'ip': ip, 'inf': informer_id, 'dt': {'$lte': click_datetime, '$gte': (click_datetime - datetime.timedelta(weeks=1))}}).limit(MAX_CLICKS_FOR_ONE_DAY + MAX_CLICKS_FOR_ONE_WEEK):
        if (click_datetime - click['dt']).days == 0:
            today_clicks += 1
            toweek_clicks += 1
        else:
            toweek_clicks +=1

        if click['offer'] == offer_id:
            unique = False

    print "Total clicks for day in informers = %s" % today_clicks
    if today_clicks >= MAX_CLICKS_FOR_ONE_DAY:
        errorId = 3
        log_reject(u'Более %d переходов с РБ за сутки' % MAX_CLICKS_FOR_ONE_DAY)
        unique = False
        print 'Many Clicks for day to informer'
        db.blacklist.ip.ensure_index('ip')
        db.blacklist.ip.update({'ip': ip},
                               {'$set': {'dt': datetime.datetime.now()}},
                               upsert=True)

    print "Total clicks for week in informers = %s" % toweek_clicks
    if toweek_clicks >= MAX_CLICKS_FOR_ONE_WEEK:
        errorId = 4
        log_reject(u'Более %d переходов с РБ за неделю' % MAX_CLICKS_FOR_ONE_WEEK)
        unique = False
        print 'Many Clicks for week to informer'
        db.blacklist.ip.ensure_index('ip')
        db.blacklist.ip.update({'ip': ip},
                               {'$set': {'dt': datetime.datetime.now()}},
                               upsert=True)
    #Проверяе по ПС за день и неделю
    today_clicks_all = 0
    toweek_clicks_all = 0
    for click in db.clicks.find({'ip': ip, 'dt': {'$lte': click_datetime, '$gte': (click_datetime - datetime.timedelta(weeks=1))}}).limit(MAX_CLICKS_FOR_ONE_WEEK_ALL + MAX_CLICKS_FOR_ONE_DAY_ALL):
        if (click_datetime - click['dt']).days == 0:
            today_clicks_all += 1
            toweek_clicks_all += 1
        else:
            toweek_clicks_all +=1

        if click['offer'] == offer_id:
            unique = False

    print "Total clicks for day in all partners = %s" % today_clicks_all
    if today_clicks_all >= MAX_CLICKS_FOR_ONE_DAY_ALL:
        errorId = 5
        log_reject(u'Более %d переходов с ПС за сутки' % MAX_CLICKS_FOR_ONE_DAY_ALL)
        unique = False
        print 'Many Clicks for day to all partners'
        db.blacklist.ip.ensure_index('ip')
        db.blacklist.ip.update({'ip': ip},
                               {'$set': {'dt': datetime.datetime.now()}},
                               upsert=True)

    print "Total clicks for week in all partners = %s" % toweek_clicks_all
    if toweek_clicks_all >= MAX_CLICKS_FOR_ONE_WEEK_ALL:
        errorId = 6
        log_reject(u'Более %d переходов с ПС за неделю' % MAX_CLICKS_FOR_ONE_WEEK_ALL)
        unique = False
        print 'Many Clicks for week to all partners'
        db.blacklist.ip.ensure_index('ip')
        db.blacklist.ip.update({'ip': ip},
                               {'$set': {'dt': datetime.datetime.now()}},
                               upsert=True)

        
    # Сохраняем клик в AdLoad
    adload_ok = True
    try:
        if unique:
            print "Adload Request"
            adload = xmlrpclib.ServerProxy(ADLOAD_XMLRPC_HOST)
            adload_response = adload.addClick(offer_id, ip)
            adload_ok = adload_response.get('ok', False)
            print "Adload OK - %s" % adload_ok
            if not adload_ok and 'error' in adload_response:
                log_error('Adload вернул ошибку: %s' %
                          adload_response['error'], campaign_id)
            adload_cost = adload_response.get('cost', 0)
            print "Adload Cost - %s" % adload_cost
    except Exception, ex:
        adload_ok = False
        log_error(u'Ошибка при обращении к adload: %s' % str(ex), campaign_id)
        print "adload failed"

    # Сохраняем клик в GetMyAd
    if not social and adload_ok:
        cost = _partner_click_cost(informer_id, adload_cost) if unique else 0
        db.clicks.insert({"ip": ip,
                          "city": city,
                          "country": country,
                          "offer": offer_id,
                          "campaignId": campaign_id,
                          "campaignTitle": campaign_title,
                          "title": title,
                          "dt": click_datetime,
                          "inf": informer_id,
                          "unique": unique,
                          "cost": cost,
                          "url": url,
                          "type": 'teaser',
                          "social":False},
                          safe=True)
        print "Payable click at the price of %s" % cost
    if social and adload_ok:
        cost = 0
        db.clicks.insert({"ip": ip,
                          "city": city,
                          "country": country,
                          "offer": offer_id,
                          "campaignId": campaign_id,
                          "campaignTitle": campaign_title,
                          "title": title,
                          "dt": click_datetime,
                          "inf": informer_id,
                          "unique": unique,
                          "cost": cost,
                          "url": url,
                          "type": 'teaser',
                          "social":True},
                          safe=True)
        print "Social click"

    print "Click complite"
    print "/----------------------------------------------------------------------/"

if __name__ == '__main__':
    db = pymongo.Connection(host=MONGO_HOST).getmyad_db 
    date = datetime.datetime(2012, 06, 28)
    clicks = db.clicks.error.find({'dt': {'$gte': date}})
    for c in clicks:    
        try:
            print c['url'], c['ip'], c['dt'], c['offer'], c['inf'], c['token'], c['server'], c['city'], c['country'], c['campaignId'] 
            process_click('url', c['ip'], c['dt'], c['offer'], c['inf'], c['token'], c['server'], c['city'], c['country'], c['campaignId'])
        except Exception as ex:
            print "Exception:", ex
    clicks = db.clicks.rejected.find({'dt': {'$gte': date}})
    for c in clicks:    
        try:
            print c['url'], c['ip'], c['dt'], c['offer'], c['inf'], c['token'], c['server'], c['city'], c['country'], c['campaignId'] 
            process_click('url', c['ip'], c['dt'], c['offer'], c['inf'], c['token'], c['server'], c['city'], c['country'], c['campaignId'])
        except Exception as ex:
            print "Exception:", ex
