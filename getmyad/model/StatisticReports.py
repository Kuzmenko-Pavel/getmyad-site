# This Python file uses the following encoding: utf-8
from pylons import app_globals
from pylons.decorators.cache import beaker_cache
from getmyad.lib import helpers as h


class StatisticReport():
    def __init__(self):
        self.db = app_globals.db

    def allAdvertiseScriptsSummary(self, user_login, dateStart=None, dateEnd=None):
        """Возвращает суммарную статистику по всем площадкам пользователя user_id"""
        reduce = '''function(o,p) {
                p.advTitle = (o.domain || " ") + (o.title || " ");
                p.clicks += o.clicks || 0;
                p.social_clicks += o.social_clicks || 0;
                p.view_seconds += o.view_seconds || 0;
                p.unique += o.clicksUnique || 0
                p.impressions_block += o.impressions_block || 0;
                p.impressions_block_not_valid += o.impressions_block_not_valid || 0;
                p.totalCost += o.totalCost || 0;
                var difference_impressions_block = 100.0;
                if (p.impressions_block_not_valid > p.impressions_block && p.impressions_block_not_valid > 0)
                {
                    difference_impressions_block = difference_impressions_block * (p.impressions_block / p.impressions_block_not_valid)
                }
                p.difference_impressions_block = difference_impressions_block;
            }'''
        condition = {'user': user_login}
        dateCondition = {}
        if dateStart <> None: dateCondition['$gte'] = dateStart
        if dateEnd <> None:   dateCondition['$lte'] = dateEnd
        if len(dateCondition) > 0:
            condition['date'] = dateCondition

        res = self.db.stats.daily.adv.group(['adv'],
                                            condition,
                                            {'advTitle': '',
                                             'clicks': 0,
                                             'social_clicks': 0,
                                             'view_seconds': 0,
                                             'unique': 0,
                                             'impressions_block': 0,
                                             'impressions_block_not_valid': 0,
                                             'difference_impressions_block': 0,
                                             'totalCost': 0},
                                            reduce)
        return res

    def statUserGroupedByDate(self, user, dateStart=None, dateEnd=None):
        """ Возвращает список {дата,уникальных,кликов,показов,сумма} 
            для пользователя или списка пользователей.
            
            Формат одной структуры в списке:
            
                {'date': datetime.datetime,
                 'unique': int,
                 'clicks': int,
                 'impressions': int,
                 'summ': float}
        
        """

        reduce = '''function(o,p) {
                p.domain = o.domain || " ";
                p.title = o.title || " ";
                p.clicks += o.clicks || 0;
                p.social_clicks += o.social_clicks || 0;
                p.view_seconds += o.view_seconds || 0;
                p.unique += o.clicksUnique || 0
                p.impressions_block += o.impressions_block || 0;
                p.impressions_block_not_valid += o.impressions_block_not_valid || 0;
                p.summ += o.totalCost || 0;
                var difference_impressions_block = 100.0;
                if (p.impressions_block_not_valid > p.impressions_block && p.impressions_block_not_valid > 0)
                {
                    difference_impressions_block = difference_impressions_block * (p.impressions_block / p.impressions_block_not_valid)
                }
                p.difference_impressions_block = difference_impressions_block;
            }'''

        condition = {'user': {'$in': user if isinstance(user, list) else [user]}}
        dateCondition = {}
        if dateStart <> None: dateCondition['$gte'] = dateStart
        if dateEnd <> None:   dateCondition['$lte'] = dateEnd
        if len(dateCondition) > 0:
            condition['date'] = dateCondition
        return [{'date': x['date'],
                 'unique': x['unique'],
                 'clicks': x['clicks'],
                 'social_clicks': x['social_clicks'],
                 'view_seconds': x['view_seconds'],
                 'impressions_block': x['impressions_block'],
                 'impressions_block_not_valid': x['impressions_block_not_valid'],
                 'difference_impressions_block': x['difference_impressions_block'],
                 'summ': x['summ']}
                for x in self.db.stats.daily.user.group(['date'],
                                                        condition,
                                                        {'clicks': 0,
                                                         'social_clicks': 0,
                                                         'view_seconds': 0,
                                                         'unique': 0,
                                                         'impressions_block': 0,
                                                         'impressions_block_not_valid': 0,
                                                         'difference_impressions_block': 0,
                                                         'summ': 0},
                                                        reduce)]

    def statAdvGroupedByDate(self, adv_guid, dateStart=None, dateEnd=None):
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

        reduce = '''function(o,p) {
                p.domain = o.domain || " ";
                p.title = o.title || " ";
                p.clicks += o.clicks || 0;
                p.social_clicks += o.social_clicks || 0;
                p.view_seconds += o.view_seconds || 0;
                p.unique += o.clicksUnique || 0
                p.impressions_block += o.impressions_block || 0;
                p.impressions_block_not_valid += o.impressions_block_not_valid || 0;
                p.summ += o.totalCost || 0;
                var difference_impressions_block = 100.0;
                if (p.impressions_block_not_valid > p.impressions_block && p.impressions_block_not_valid > 0)
                {
                    difference_impressions_block = difference_impressions_block * (p.impressions_block / p.impressions_block_not_valid)
                }
                p.difference_impressions_block = difference_impressions_block;
            }'''

        condition = {'adv': adv_guid}
        dateCondition = {}
        if dateStart <> None: dateCondition['$gte'] = dateStart
        if dateEnd <> None:   dateCondition['$lte'] = dateEnd
        if len(dateCondition) > 0:
            condition['date'] = dateCondition

        return [{'date': x['date'],
                 'unique': x['unique'],
                 'clicks': x['clicks'],
                 'social_clicks': x['social_clicks'],
                 'view_seconds': x['view_seconds'],
                 'impressions_block': x['impressions_block'],
                 'impressions_block_not_valid': x['impressions_block_not_valid'],
                 'difference_impressions_block': x['difference_impressions_block'],
                 'summ': x['summ']}
                for x in self.db.stats.daily.adv.group(['date'],
                                                       condition,
                                                       {'clicks': 0,
                                                        'social_clicks': 0,
                                                        'view_seconds': 0,
                                                        'unique': 0,
                                                        'impressions_block': 0,
                                                        'impressions_block_not_valid': 0,
                                                        'difference_impressions_block': 0,
                                                        'summ': 0},
                                                       reduce)]

    def statAdvByDate(self, user, dateStart=None, dateEnd=None):
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

        reduce = '''function(o,p) {
                p.clicks += o.clicks || 0;
                p.domain = o.domain || " ";
                p.title = o.title || " ";
                p.data.push([ (o.date) ,(o.totalCost || 0)]);
            }'''

        condition = {'user': user}
        dateCondition = {}
        if dateStart <> None: dateCondition['$gte'] = dateStart
        if dateEnd <> None:   dateCondition['$lte'] = dateEnd
        if len(dateCondition) > 0:
            condition['date'] = dateCondition

        return [{'guid': x['adv'],
                 'domain': x['domain'],
                 'title': x['title'],
                 'data': x['data']}
                for x in self.db.stats.daily.adv.group(['adv'],
                                                       condition,
                                                       {'title': '', 'domain': '', 'data': []},
                                                       reduce)]
