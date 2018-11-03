# -*- coding: UTF-8 -*-
import logging
import uuid
import time
import shelve
import os

from pylons import app_globals

log = logging.getLogger(__name__)


class AdloadData(object):
    'Класс предоставляет интерфейс для взаимодействия и управления ``AdLoad``'

    __slots__ = ['connection_adload', '_shelve_file', 'offers']

    def __init__(self, connection_adload=None):
        if connection_adload is None:
            self.connection_adload = app_globals.connection_adload
        else:
            self.connection_adload = connection_adload
        self._shelve_file = uuid.uuid4().get_hex() + '.shelve'
        print(__file__)
        print(self._shelve_file)
        self.offers = shelve.open(self._shelve_file)

    def __enter__(self):
        """

        Returns:

        """
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        """

        Args:
            ext_type:
            exc_value:
            traceback:
        """
        try:
            os.remove(self._shelve_file)
        except OSError as e:
            print e
            pass

    def __del__(self):
        """

        Args:
            ext_type:
            exc_value:
            traceback:
        """
        try:
            os.remove(self._shelve_file)
        except OSError as e:
            print e
            pass

    def offer_count(self, campaign):
        print 'Count Offers from ', campaign
        try:
            count = 0
            print 'Find Adload count'
            print campaign
            cursor_a = self.connection_adload.cursor()
            # Частные предложения (информеры)
            cursor_a.execute('''
                SELECT count(*) AS count
                FROM View_Lot 
                INNER JOIN LotByAdvertise ON LotByAdvertise.LotID = View_Lot.LotID
                WHERE LotByAdvertise.AdvertiseID = %s AND View_Lot.ExternalURL <> '' 
                    AND View_Lot.isTest = 1 AND View_Lot.isAdvertising = 1
                ''', campaign)
            for row in cursor_a:
                count += int(row.get('count', 0))
            cursor_a.close()
            print count
            return count
        except Exception, ex:
            print ex
            return 0

    def offers_list(self, campaign, load_count=100):
        print 'Get Offers'
        start_time_main = time.time()
        """ Возвращает список активных рекламных предложений,
            относящихся к рекламной кампании ``campaign``. 

            Ответ имеет следующий формат::

                (array)
                    (struct)
                        'id':          (string),
                        'accountId'    (string),
                        'title':       (string),
                        'price':       (string),
                        'url':         (string),
                        'image':       (string),
                        'description': (string),
                        'dateAdded':   (string),
                        'ClickCost':   (string)
                    (struct-end)
                (array-end)
        
         """
        try:
            currency_cost = self._currencyCostCached('$')
            print 'Find Adload'
            cursor_a = self.connection_adload.cursor()
            # Частные предложения (информеры)
            cursor_a.execute('''
                SELECT TOP %s  View_Lot.LotID AS LotID,
                View_Lot.Title AS Title,
                View_Lot.RetargetingID AS RetargetingID,
                View_Lot.ExternalURL AS UrlToMarket,
                View_Lot.ClickCost, 
                ISNULL(View_Lot.Descript, '') AS About,
                View_Lot.ImgURL 
                ,ISNULL(View_Lot.Logo, '') Logo
                ,ISNULL(View_Lot.Price, '') Price
                ,View_Advertise.UserID AS UserID
                ,View_Lot.Recommended AS Recommended
                FROM View_Lot 
                INNER JOIN LotByAdvertise ON LotByAdvertise.LotID = View_Lot.LotID
                INNER JOIN View_Advertise ON View_Advertise.AdvertiseID = LotByAdvertise.AdvertiseID
                WHERE View_Advertise.AdvertiseID = %s AND View_Lot.ExternalURL <> '' 
                    AND View_Lot.isTest = 1 AND View_Lot.isAdvertising = 1
                ''', (load_count, campaign))
            for row in cursor_a:
                click_cost = float(row['ClickCost'])
                if currency_cost > 0:
                    click_cost /= currency_cost
                data = {}
                data['id'] = str(row['LotID']).lower()
                data['accountId'] = str(row['UserID']).lower()
                data['title'] = row['Title']
                data['price'] = row['Price']
                data['url'] = row['UrlToMarket']
                data['image'] = row['ImgURL']
                data['logo'] = row['Logo']
                data['description'] = row['About']
                data['RetargetingID'] = row.get('RetargetingID', '').strip()
                data['Recommended'] = row['Recommended']
                try:
                    data['ClickCost'] = float(click_cost)
                except Exception as e:
                    print (e)
                    data['ClickCost'] = 0.0
                self.offers[data['id']] = data
            cursor_a.close()
            # app_globals.connection_adload.close()
            print 'Connection Adload closed'
        except Exception, ex:
            raise
        print("--- Get Offers %s seconds ---" % (time.time() - start_time_main))

    offers_list.signature = [['struct', 'string']]

    def campaigns_list(self):
        """Возвращает список всех активных рекламных кампаний.
        
        Ответ имеет следующий формат::

            (array)
                (struct)
                    'id':      (string)
                    'user':    (string)
                    'user_name':(string)
                    'title':   (string)
                    'getmyad': (bool) 
                (struct-end)
            (array-end)
        
        ``getmyad`` показывает, рекламируется ли кампания в GetMyAd или нет.
        """
        cursor = self.connection_adload.cursor()
        cursor.execute('''SELECT a.AdvertiseID AS AdvertiseID, a.UserID, Title, Login, m.Name AS Manager,
                            CASE WHEN ag.AdvertiseID IS NULL THEN 0 ELSE 1 END AS InGetMyAd
                        FROM View_Advertise a
                        LEFT OUTER JOIN AdvertiseInGetMyAd ag ON ag.AdvertiseID = a.AdvertiseID
                        LEFT OUTER JOIN Users u ON u.UserID = a.UserID
                        LEFT OUTER JOIN Manager m  ON u.ManagerID = m.id
                        WHERE m.Name IS NOT NULL AND isActive=1 ORDER BY Title''')
        result = []
        for row in cursor:
            id = str(row['AdvertiseID']).lower()
            if id in app_globals.hidden_campaign:
                continue
            adv = {'id': id,
                   'user': str(row['UserID']).lower(),
                   'user_name': row['Login'],
                   'manager': row['Manager'],
                   'title': row['Title'],
                   'getmyad': bool(row['InGetMyAd'])
                   }
            result.append(adv)
        cursor.close()
        # app_globals.connection_adload.close()
        return result

    campaigns_list.signature = [['array']]

    def campaign_details(self, campaign):
        ''' Возвращает подробную информацию о кампании ``campaign``.
        Формат ответа::
            
            (struct)
                'id':      (string)
                'title':   (string)
                'getmyad': (bool)
            (struct-end)
        '''
        cursor = self.connection_adload.cursor()
        cursor.execute('''SELECT a.AdvertiseId AS AdvertiseID, a.UserID AS UserID, Title, m.Name AS Manager, 
                            CASE WHEN ag.AdvertiseID IS NULL THEN 0 ELSE 1 END AS InGetMyAd
                        FROM View_Advertise a
                        LEFT OUTER JOIN AdvertiseInGetMyAd ag ON ag.AdvertiseID = a.AdvertiseID
                        LEFT OUTER JOIN Users u ON u.UserID = a.UserID
                        LEFT OUTER JOIN Manager m  ON u.ManagerID = m.id
                        WHERE a.AdvertiseID = %s''', campaign)
        row = cursor.fetchone()
        if not row:
            cursor.close()
            # app_globals.connection_adload.close()
            return {}
        cursor.close()
        # app_globals.connection_adload.close()
        return {'id': str(row['AdvertiseID']).lower(),
                'title': row['Title'],
                'account': str(row['UserID']).lower(),
                'manager': row.get('Manager', ''),
                'getmyad': bool(row['InGetMyAd'])
                }

    campaign_details.signature = [['struct', 'string']]

    def campaign_check(self, campaign):
        ''' Возвращает подробную информацию о кампании ``campaign``.
        Формат ответа::
        '''
        cursor = self.connection_adload.cursor()
        cursor.execute('''SELECT isActive
                        FROM View_Advertise
                        WHERE isActive = 1 AND AdvertiseID = %s''', campaign)
        row = cursor.fetchone()
        if not row:
            cursor.close()
            # app_globals.connection_adload.close()
            return {'ok': False}
        cursor.close()
        # app_globals.connection_adload.close()
        return {'ok': True}

    def campaign_addToGetmyad(self, campaign_id):
        ''' Добавляет кампанию ``campaign_id`` в список кампаний, которые должны рекламироваться в GetMyAd '''
        cursor = self.connection_adload.cursor()
        cursor.execute('SELECT count(*) AS cnt FROM AdvertiseInGetMyAd WHERE AdvertiseID=%s', campaign_id)
        if cursor.fetchone()['cnt']:
            cursor.close()
            # app_globals.connection_adload.close()
            return {'ok': True, 'warning': 'Campaign already in getmyad'}
        cursor.execute('INSERT INTO AdvertiseInGetMyAd(AdvertiseID) VALUES (%s)', campaign_id)
        cursor.close()
        # app_globals.connection_adload.close()
        return {'ok': True}

    def campaign_removeFromGetmyad(self, campaign_id):
        ''' Убирает кампанию ``campaign_id`` из списка кампаний, которые должны рекламироваться в GetMyAd '''
        cursor = self.connection_adload.cursor()
        cursor.execute('SELECT count(*) AS cnt FROM AdvertiseInGetMyAd WHERE AdvertiseID=%s', campaign_id)
        if not cursor.fetchone()['cnt']:
            cursor.close()
            # app_globals.connection_adload.close()
            return {'ok': True, 'warning': 'Campaign wasn\'t mark for getmyad advertising'}
        cursor.execute('DELETE FROM AdvertiseInGetMyAd WHERE AdvertiseID = %s', campaign_id)
        cursor.close()
        # app_globals.connection_adload.close()
        return {'ok': True}

    def currencyCost(self, currency):
        ''' Возвращает курс валюты ``currency``.

            Если валюта не найдена, вернёт 0.
        '''
        cursor = self.connection_adload.cursor()
        cursor.execute('SELECT cost FROM GetMyAd_CurrencyCost WHERE currency=%s', (currency,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            # app_globals.connection_adload.close()
            return 0.0
        cursor.close()
        # app_globals.connection_adload.close()
        return float(row['cost'])

    currencyCost.signature = [['double', 'string']]

    def setCurrencyCost(self, currency, cost):
        ''' Устанавливает курс валюты ``currency`` равным ``cost``. '''
        cursor = self.connection_adload.cursor()
        cursor.execute('DELETE FROM GetMyAd_CurrencyCost WHERE currency=%s', (currency,))
        cursor.execute('INSERT INTO GetMyAd_CurrencyCost (currency, cost) VALUES (%s, %s)', (currency, cost))
        cursor.close()
        # app_globals.connection_adload.close()
        return True

    setCurrencyCost.signature = [['boolean', 'string', 'double'],
                                 ['boolean', 'string', 'int']]

    def _currencyCostCached(self, currency):
        ''' Возвращает курс валюты ``currency``.
        
            Кеширует результат в памяти.
        '''
        return self.currencyCost(currency)

    def clickCost(self, offer_id):
        log.info("Click Cost")
        ''' Получение цены за  рекламное предложение ``offer_id``.

            ``offer_id``
                GUID рекламного предложения.

            Возвращает структуру следующего формата::
                
                {'ok': Boolean,     # Успешно ли выполнилась операция
                 'error': String,   # Описание ошибки, если ok == False
                 'cost': Decimal    # Сумма, списанная с рекламодателя (в $)
                }
        '''
        print 'Get ClickCost'
        try:
            uuid.UUID(offer_id)
        except ValueError, ex:
            log.debug(ex)
            return {'ok': False, 'error': 'offer_id should be uuid string!'}

        try:
            cursor = self.connection_adload.cursor()
            click_cost = 0.0
            # Ищем в частных предложениях    
            cursor.execute('''
                SELECT ClickCost FROM Lot
                WHERE LotID=%s AND isAdvertising=1 AND isBlock=0 AND isTest=1''',
                           offer_id)
            try:
                row = cursor.fetchone()
                click_cost = float(row['ClickCost'])
            except Exception, ex:
                log.debug(ex)

            # Пересчёт стоимости клика по курсу
            currency_cost = self._currencyCostCached('$')
            if currency_cost > 0:
                click_cost /= currency_cost
            cursor.close()
            # app_globals.connection_adload.close()
            return {'ok': True, 'cost': click_cost}

        except Exception, ex:
            log.debug(ex)
            cursor.close()
            # app_globals.connection_adload.close()
            return {'ok': False, 'error': str(ex)}
