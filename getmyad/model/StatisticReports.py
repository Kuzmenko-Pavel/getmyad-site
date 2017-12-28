# -*- coding: UTF-8 -*-
from pylons import app_globals


class StatisticReport():
    
    def __init__(self):
        self.db = app_globals.db
    
    def allAdvertiseScriptsSummary(self, user_login, dateStart = None, dateEnd = None):
        """Возвращает суммарную статистику по всем площадкам пользователя user_id"""
        res = []
        condition = {'user': user_login}
        dateCondition = {}
        if dateStart <> None: dateCondition['$gte'] = dateStart
        if dateEnd <> None:   dateCondition['$lte'] = dateEnd
        if len(dateCondition) > 0:
            condition['date'] = dateCondition
        pipeline = [{'$match': condition},
                    {'$group': {
                        '_id': '$adv',
                        'domain': {'$last': '$domain'},
                        'title': {'$last': '$title'},
                        'clicks': {'$sum': '$clicks'},
                        'social_clicks': {'$sum': '$social_clicks'},
                        'view_seconds': {'$sum': '$view_seconds'},
                        'unique': {'$sum': '$clicksUnique'},
                        'impressions_block': {'$sum': '$impressions_block'},
                        'impressions_block_not_valid': {'$sum': '$impressions_block_not_valid'},
                        'totalCost': {'$sum': '$totalCost'}
                    }}
                    ]
        cursor = self.db.stats.daily.adv.aggregate(pipeline=pipeline)
        for x in cursor:
            d = {}
            d['adv'] = x['_id']
            d['advTitle'] = x['domain'] + x['title']
            d['clicks'] = float(x['clicks'])
            d['social_clicks'] = float(x['social_clicks'])
            d['view_seconds'] = float(x['view_seconds'])
            d['unique'] = float(x['unique'])
            d['impressions_block'] = float(x['impressions_block'])
            d['impressions_block_not_valid'] = float(x['impressions_block_not_valid'])
            d['totalCost'] = float(x['totalCost'])
            d['difference_impressions_block'] = 100.0
            if d['impressions_block_not_valid'] > d['impressions_block'] and d['impressions_block_not_valid'] > 0:
                d['difference_impressions_block'] = d['difference_impressions_block'] * (d['impressions_block'] / d['impressions_block_not_valid'])
            res.append(d)
        return res

    def statUserGroupedByDate(self, user, dateStart = None, dateEnd = None):
        """ Возвращает список {дата,уникальных,кликов,показов,сумма} 
            для пользователя или списка пользователей.
            
            Формат одной структуры в списке:
            
                {'date': datetime.datetime,
                 'unique': int,
                 'clicks': int,
                 'impressions': int,
                 'summ': float}
        
        """
        res = []
        condition = {'user': {'$in': user if isinstance(user, list) else [user]}}
        dateCondition = {}
        if dateStart <> None: dateCondition['$gte'] = dateStart
        if dateEnd <> None:   dateCondition['$lte'] = dateEnd
        if len(dateCondition) > 0:
            condition['date'] = dateCondition

        pipeline = [{'$match': condition},
                    {'$group': {
                        '_id': '$date',
                        'clicks': {'$sum': '$clicks'},
                        'social_clicks': {'$sum': '$social_clicks'},
                        'view_seconds': {'$sum': '$view_seconds'},
                        'unique': {'$sum': '$clicksUnique'},
                        'impressions_block': {'$sum': '$impressions_block'},
                        'impressions_block_not_valid': {'$sum': '$impressions_block_not_valid'},
                        'summ': {'$sum': '$totalCost'}
                    }}
                    ]
        cursor = self.db.stats.daily.user.aggregate(pipeline=pipeline)
        for x in cursor:
            d = {}
            d['date'] = x['_id']
            d['clicks'] = float(x['clicks'])
            d['social_clicks'] = float(x['social_clicks'])
            d['view_seconds'] = float(x['view_seconds'])
            d['unique'] = float(x['unique'])
            d['impressions_block'] = float(x['impressions_block'])
            d['impressions_block_not_valid'] = float(x['impressions_block_not_valid'])
            d['summ'] = float(x['summ'])
            d['difference_impressions_block'] = 100.0
            if d['impressions_block_not_valid'] > d['impressions_block'] and d['impressions_block_not_valid'] > 0:
                d['difference_impressions_block'] = d['difference_impressions_block'] * (
                d['impressions_block'] / d['impressions_block_not_valid'])
            res.append(d)

        return res

    def statAdvGroupedByDate(self, adv_guid, dateStart = None, dateEnd = None):
        """ Возвращает список {дата,уникальных,кликов,показов,сумма} 
            для одного РБ.
            
            Формат одной структуры в списке:
            
                {'date': datetime.datetime,
                 'unique': int,
                 'clicks': int,
                 'impressions': int,
                 'summ': float}
        
            Параметр adv_guid -- коды одного РБ,
            по которым будет считаться статистика.
        """
        res = []
        condition = {'adv': adv_guid }
        dateCondition = {}
        if dateStart <> None: dateCondition['$gte'] = dateStart
        if dateEnd <> None:   dateCondition['$lte'] = dateEnd
        if len(dateCondition) > 0:
            condition['date'] = dateCondition

        pipeline = [{'$match': condition},
                    {'$group': {
                        '_id': '$date',
                        'clicks': {'$sum': '$clicks'},
                        'social_clicks': {'$sum': '$social_clicks'},
                        'view_seconds': {'$sum': '$view_seconds'},
                        'unique': {'$sum': '$clicksUnique'},
                        'impressions_block': {'$sum': '$impressions_block'},
                        'impressions_block_not_valid': {'$sum': '$impressions_block_not_valid'},
                        'summ': {'$sum': '$totalCost'}
                    }}
                    ]
        cursor = self.db.stats.daily.adv.aggregate(pipeline=pipeline)
        for x in cursor:
            d = {}
            d['date'] = x['_id']
            d['clicks'] = float(x['clicks'])
            d['social_clicks'] = float(x['social_clicks'])
            d['view_seconds'] = float(x['view_seconds'])
            d['unique'] = float(x['unique'])
            d['impressions_block'] = float(x['impressions_block'])
            d['impressions_block_not_valid'] = float(x['impressions_block_not_valid'])
            d['summ'] = float(x['summ'])
            d['difference_impressions_block'] = 100.0
            if d['impressions_block_not_valid'] > d['impressions_block'] and d['impressions_block_not_valid'] > 0:
                d['difference_impressions_block'] = d['difference_impressions_block'] * (
                    d['impressions_block'] / d['impressions_block_not_valid'])
            res.append(d)

        return res

    def statAdvByDate(self, user, dateStart = None, dateEnd = None):
        """ Возвращает список {дата,уникальных,кликов,показов,сумма} 
            для пользователя.
            
            Формат одной структуры в списке:
            
                {'date': datetime.datetime,
                 'unique': int,
                 'clicks': int,
                 'impressions': int,
                 'summ': float}
        
            Параметр adv_guid -- нескольких РБ,
            по которым будет считаться статистика.
        """
        res = []
        condition = {'user': user}
        dateCondition = {}
        if dateStart <> None: dateCondition['$gte'] = dateStart
        if dateEnd <> None:   dateCondition['$lte'] = dateEnd
        if len(dateCondition) > 0:
            condition['date'] = dateCondition

        pipeline = [{'$match': condition},
                    {'$group': {
                        '_id': '$adv',
                        'clicks': {'$sum': '$clicks'},
                        'domain': {'$last': '$domain'},
                        'title': {'$last': '$title'},
                        'data': {'$push': {'date':'$date', 'totalCost': '$totalCost'}}
                    }}]
        cursor = self.db.stats.daily.adv.aggregate(pipeline=pipeline)
        for x in cursor:
            res.append(
                {'guid': x['_id'],
                 'domain': x['domain'],
                 'title': x['title'],
                 'data': [ [i['date'], i['totalCost']] for i in x['data']]
            }
            )
        return res
