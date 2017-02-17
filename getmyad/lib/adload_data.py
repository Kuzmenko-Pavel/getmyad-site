# encoding: utf-8
from pylons import app_globals
import logging
import datetime
import uuid
import dateutil.parser

log = logging.getLogger(__name__)

class AdloadData(object):
    'Класс предоставляет интерфейс для взаимодействия и управления ``AdLoad``'
    def __init__(self, connection_adload=None):
        if connection_adload is None:
            self.connection_adload = app_globals.connection_adload
        else:
            self.connection_adload = connection_adload

    def offer_count(self, campaign):
        print 'Count Offers from ', campaign
        try:
            count = 0
            print 'Find Adload count'
            print campaign
            cursor_a = self.connection_adload.cursor()
            # Частные предложения (информеры)
            cursor_a.execute('''
                select count(*) AS count
                from Lot 
                inner join LotByAdvertise on LotByAdvertise.LotID = Lot.LotID
                where LotByAdvertise.AdvertiseID = %s and Lot.ExternalURL <> '' 
                    and Lot.isTest = 1 and lot.isAdvertising = 1
                ''', campaign)
            for row in cursor_a:
                count += int(row.get('count',0))
            cursor_a.close()
            print count
            return count
        except Exception, ex:
            print ex
            return 0

    def offers_list(self, campaign, load_count=100):
        print 'Get Offers'
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
            offers = []
            print 'Find Adload'
            cursor_a = self.connection_adload.cursor()
            # Частные предложения (информеры)
            cursor_a.execute('''
                select TOP %s  Lot.LotID as LotID, Lot.Title as Title, Lot.RetargetingID as RetargetingID, ExternalURL as UrlToMarket, [ClickCost], 
                    isnull(Lot.Descript, '') as About,
                    Lot.ImgURL 
                    ,ISNULL(lot.Logo, '') Logo
                    ,ISNULL(lot.Price, '') Price
                    ,Lot.DateCreate as DateAdvert
                    ,Advertise.UserID as UserID
                    ,Lot.Recommended as Recommended
                from Lot 
                inner join LotByAdvertise on LotByAdvertise.LotID = Lot.LotID
                inner join Advertise on Advertise.AdvertiseID = LotByAdvertise.AdvertiseID
                where Advertise.AdvertiseID = %s and Lot.ExternalURL <> '' 
                    and Lot.isTest = 1 and lot.isAdvertising = 1
                ''', (load_count,  campaign))
            for row in cursor_a:
                click_cost = float(row['ClickCost'])
                if currency_cost > 0:
                    click_cost /= currency_cost
                offer = {'id': str(row['LotID']).lower(),
                         'accountId': str(row['UserID']).lower(),
                         'title': row['Title'],
                         'price': row['Price'],
                         'url': row['UrlToMarket'],
                         'image': row['ImgURL'],
                         'logo': row['Logo'],
                         'description': row['About'],
                         'dateAdded': row['DateAdvert'],
                         'RetargetingID': row.get('RetargetingID',''),
                         'Recommended': row['Recommended'],
                         'ClickCost': str(click_cost)
                        }
                offers.append(offer)
            cursor_a.close()
            #app_globals.connection_adload.close()
            print 'Connection Adload closed'
            return offers
        except Exception, ex:
            raise
            return "Server-side exception has occured: " + str(ex)
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
        cursor.execute('''select a.AdvertiseID as AdvertiseID, a.UserID, Title, Login, m.Name as Manager,
                            case when ag.AdvertiseID is null then 0 else 1 end as InGetMyAd
                        from Advertise a
                        left outer join AdvertiseInGetMyAd ag on ag.AdvertiseID = a.AdvertiseID
                        left outer join Users u on u.UserID = a.UserID
                        left outer join Manager m  on u.ManagerID = m.id
                        where m.Name is not Null and isActive=1 order by Title''')
        result = []
        for row in cursor:
            adv = {'id': str(row['AdvertiseID']).lower(),
                   'user': str(row['UserID']).lower(),
                   'user_name': row['Login'],
                   'manager': row.get('Manager',''),
                   'title': row['Title'],
                   'getmyad': bool(row['InGetMyAd'])                   
                  }
            result.append(adv)
        cursor.close()
        #app_globals.connection_adload.close()
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
        cursor.execute('''select a.AdvertiseId as AdvertiseID, a.UserID as UserID, Title, m.Name as Manager, 
                            case when ag.AdvertiseID is null then 0 else 1 end as InGetMyAd
                        from Advertise a
                        left outer join AdvertiseInGetMyAd ag on ag.AdvertiseID = a.AdvertiseID
                        left outer join Users u on u.UserID = a.UserID
                        left outer join Manager m  on u.ManagerID = m.id
                        where a.AdvertiseID = %s''', campaign)
        row = cursor.fetchone()
        if not row:
            cursor.close()
            #app_globals.connection_adload.close()
            return {}
        cursor.close()
        #app_globals.connection_adload.close()
        return {'id': str(row['AdvertiseID']).lower(),
                'title': row['Title'],
                'account': str(row['UserID']).lower(),
                'manager': row.get('Manager',''),
                'getmyad': bool(row['InGetMyAd'])
                }
    campaign_details.signature = [['struct', 'string']]
   
    def campaign_check(self, campaign):
        ''' Возвращает подробную информацию о кампании ``campaign``.
        Формат ответа::
        '''
        cursor = self.connection_adload.cursor()
        cursor.execute('''select isActive
                        from Advertise
                        where isActive = 1 and AdvertiseID = %s''', campaign)
        row = cursor.fetchone()
        if not row:
            cursor.close()
            #app_globals.connection_adload.close()
            return {'ok': False}
        cursor.close()
        #app_globals.connection_adload.close()
        return {'ok': True}
    
    def campaign_addToGetmyad(self, campaign_id):
        ''' Добавляет кампанию ``campaign_id`` в список кампаний, которые должны рекламироваться в GetMyAd '''
        cursor = self.connection_adload.cursor()
        cursor.execute('select count(*) as cnt from AdvertiseInGetMyAd where AdvertiseID=%s', campaign_id)
        if cursor.fetchone()['cnt']:
            cursor.close()
            #app_globals.connection_adload.close()
            return {'ok': True, 'warning': 'Campaign already in getmyad'}
        cursor.execute('insert into AdvertiseInGetMyAd(AdvertiseID) values (%s)', campaign_id)
        cursor.close()
        #app_globals.connection_adload.close()
        return {'ok': True}
    
    def campaign_removeFromGetmyad(self, campaign_id):
        ''' Убирает кампанию ``campaign_id`` из списка кампаний, которые должны рекламироваться в GetMyAd '''
        cursor = self.connection_adload.cursor()
        cursor.execute('select count(*) as cnt from AdvertiseInGetMyAd where AdvertiseID=%s', campaign_id)
        if not cursor.fetchone()['cnt']:
            cursor.close()
            #app_globals.connection_adload.close()
            return {'ok': True, 'warning': 'Campaign wasn\'t mark for getmyad advertising'}
        cursor.execute('delete from AdvertiseInGetMyAd where AdvertiseID = %s', campaign_id)
        cursor.close()
        #app_globals.connection_adload.close()
        return {'ok': True}

    def currencyCost(self, currency):
        ''' Возвращает курс валюты ``currency``.

            Если валюта не найдена, вернёт 0.
        '''
        cursor = self.connection_adload.cursor()
        cursor.execute('select cost from GetMyAd_CurrencyCost where currency=%s', (currency,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            #app_globals.connection_adload.close()
            return 0.0
        cursor.close()
        #app_globals.connection_adload.close()
        return float(row['cost'])
    currencyCost.signature = [['double', 'string']]


    def setCurrencyCost(self, currency, cost):
        ''' Устанавливает курс валюты ``currency`` равным ``cost``. '''
        cursor = self.connection_adload.cursor()
        cursor.execute('delete from GetMyAd_CurrencyCost where currency=%s', (currency, ))
        cursor.execute('insert into GetMyAd_CurrencyCost (currency, cost) values (%s, %s)', (currency, cost))
        cursor.close()
        #app_globals.connection_adload.close()
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
                select ClickCost from Lot
                where LotID=%s and isAdvertising=1 and isBlock=0 and isTest=1''',
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
            #app_globals.connection_adload.close()
            return {'ok': True, 'cost': click_cost}
        
        except Exception, ex:
            log.debug(ex)
            cursor.close()
            #app_globals.connection_adload.close()
            return {'ok': False, 'error': str(ex)}
