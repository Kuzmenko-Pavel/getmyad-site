# encoding: utf-8

import base64
import datetime
import fileinput
import xmlrpclib

import pymongo
import re

MONGO_MAIN_HOST = 'yottos.com'
ADLOAD_XMLRPC_HOST = 'http://adload.vsrv-1.2.yottos.com/rpc'

class ClicksLogParser():
    def __init__(self, mongo_host):
        self.db = pymongo.Connection(mongo_host).getmyad_db
        self.social = self._social_offers()
        self.ok_count = 0
        self.failed_count = 0
        self.social_count = 0
        self.not_unique_count = 0

    def process_log_line(self, line):
        row = re.match(r'(?P<ip>\d+\.\d+.\d+.\d+) - - '
                       r'\[(?P<date>.*)\] \"GET /redirect\?(?P<query>[^ ]+)',
                       line)
        if not row:
            return
        dt = datetime.datetime.strptime(row.group('date').partition(' ')[0],
                                        '%d/%b/%Y:%H:%M:%S')
        ip = row.group('ip')
        query = row.group('query')
    
        # Получаем словарь параметров
        base64_encoded_params = query.partition('&')[0]
        try:
            param_lines = base64.urlsafe_b64decode(base64_encoded_params).splitlines()
        except TypeError:
            self.failed_count += 1
            return
        params = dict([(x.partition('=')[0], x.partition('=')[2])
                       for x in param_lines])
        offer_id = params.get('id')
        informer_id = params.get('inf')
        url = params.get('url')
        self._save_click(ip, dt, offer_id, informer_id, url)

    def _save_click(self, ip, dt, offer_id, informer_id, url):
        ''' Обрабатывает клик с заданными параметрами '''
        if offer_id in self.social:
            self.social_count += 1
            return False

        if not self._click_unique(ip, dt, offer_id):
            self.not_unique_count += 1
            return False

        try:
            title = self.db.offer.find_one({'guid': offer_id})['title']
        except (TypeError, KeyError):
            title = '-'

        if not self._save_to_adload(offer_id, ip):
            self.failed_count += 1
            return False

        # Сохраняем клик в GetMyAd
        self.db.clicks.insert({"ip": ip,
                          "offer": offer_id,
                          "title": title,
                          "dt": dt,
                          "inf": informer_id,
                          "unique": True,
                          "cost": self._click_cost(informer_id, dt),
                          "url": url},
                          safe=True)
        self.ok_count += 1
        return True

    def status(self):
        return "%d total: %d ok, %d failed, %d social, %d not unique" % (
            self.ok_count + self.failed_count + self.social_count + self.not_unique_count,
            self.ok_count, self.failed_count, self.social_count, self.not_unique_count)

    def _social_offers(self):
        ''' Возвращает список guid'ов социальных предложений '''
        camps = [x['guid'] for x in self.db.campaign.find({'social': True})]
        return [x['guid']
                for x in self.db.offer.find({'campaignId': {'$in': camps}})]

    def _click_unique(self, ip, dt, offer_id):
        ''' Возвращает True, если клик уникальный. '''
        MAX_CLICKS_FOR_ONE_DAY = 3
        today_clicks = 0
        unique = True
        for click in self.db.clicks.find({'ip': ip}).sort("$natural", pymongo.DESCENDING):
            if (dt - click['dt']).days == 0:
                today_clicks += 1
            if click['offer'] == offer_id:
                unique = False
        if today_clicks > MAX_CLICKS_FOR_ONE_DAY:
            unique = False
        return unique

    def _click_cost(self, informer_id, click_datetime):
        ''' Возвращает цену клика для сайта партнёра '''
        # TODO: Плавающая цена за клик
        raise NotImplementedError()
        try:
            db = self.db
            user = db.informer.find_one({'guid': informer_id}, ['user'])['user']
            cursor = db.click_cost.find({'user.login': user,
                                         'date': {'$lte': click_datetime}}).sort('date', pymongo.DESCENDING).limit(1)
            cost = float(cursor[0]['cost'])
        except:
            cost = 0
        return cost

    def _save_to_adload(self, offer_id, ip):
        ''' Сохраняет клик в AdLoad '''
        adload_ok = True
        try:
            adload = xmlrpclib.ServerProxy(ADLOAD_XMLRPC_HOST)
            adload_response = adload.addClick(offer_id, ip)
            adload_ok = adload_response.get('ok', False)
            if not adload_ok and 'error' in adload_response:
                print 'Adload вернул ошибку: %s' % adload_response['error']
        except Exception, ex:
            adload_ok = False
            print u'Ошибка при обращении к adload: %s' % str(ex)
        return adload_ok
    
    
# TODO: Плавающая цена за клик
raise NotImplementedError()

parser = ClicksLogParser(MONGO_MAIN_HOST)
i = 0
for line in fileinput.input():
    parser.process_log_line(line)
    i += 1
    if not i % 20:
        print parser.status()

print parser.status()
