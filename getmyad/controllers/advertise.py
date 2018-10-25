# -*- coding: UTF-8 -*-
import json
import logging
import time
from datetime import datetime

import bson.json_util
from pylons import request, session, tmpl_context as c, app_globals
from pylons.controllers.util import redirect
from routes.util import url_for
from webhelpers.html.builder import escape

import getmyad.lib.helpers as h
import getmyad.model as model
from getmyad.lib.base import BaseController, render

log = logging.getLogger(__name__)


def dateFromStr(str):
    try:
        day = int(str[0:2])
        month = int(str[3:5])
        year = int(str[6:10])
        return datetime(year, month, day)
    except:
        return None


class AdvertiseController(BaseController):
    def __before__(self, action, **params):
        user = session.get('user')
        if user:
            request.environ['CURRENT_USER'] = user
            request.environ['IS_MANAGER'] = session.get('isManager', False)

    def maker(self, id):
        if not session.get('user'):
            return redirect('/')

        if not id:
            return u"Не указан id выгрузки!"

        adv = app_globals.db.informer.find_one({'guid': id})

        if not adv:
            return u"Не найдена указанная выгрузка!"

        t = adv.get('admaker')
        c.admaker = h.JSON(t) if t else None
        c.adv_id = id
        c.dynamic = str(adv.get('dynamic', False)).lower()
        c.html_notification = str(adv.get('html_notification', False)).lower()
        c.plase_branch = str(adv.get('plase_branch', True)).lower()
        c.auto_reload = adv.get('auto_reload', 0)
        c.blinking = adv.get('blinking', 0)
        c.shake = adv.get('shake', 0)
        c.rating_division = adv.get('rating_division', 1000)
        c.blinking_reload = str(adv.get('blinking_reload', False)).lower()
        c.shake_reload = str(adv.get('shake_reload', False)).lower()
        c.shake_mouse = str(adv.get('shake_mouse', False)).lower()
        c.retargeting_branch = str(adv.get('retargeting_branch', True)).lower()
        c.non_relevant = adv.get('nonRelevant', {})
        c.non_relevant['userCode'] = escape(adv.get('nonRelevant', {}).get('userCode', ''))
        c.non_relevant = h.JSON(c.non_relevant)
        return render('/admaker.mako.html')

    def pattern_maker(self, id):
        if not session.get('user'):
            return redirect('/')

        if not id:
            return u"Не указан id выгрузки!"

        adv = app_globals.db.informer.patterns.find_one({'guid': id})

        if not adv:
            return u"Не найдена указанная выгрузка!"

        t = adv.get('admaker')
        c.admaker = h.JSON(t) if t else None
        c.adv_id = id

        return render('/patternmaker.mako.html')

    def save(self):
        try:
            user = session.get('user')
            isManager = session.get('isManager', False)
            if not user:
                return h.JSON({'error': True, 'message': u'Не выполнен вход'})
            id = request.params.get('adv_id')
            object = json.loads(request.body)
            informer = model.Informer()
            informer.loadGuid(id)
            informer.guid = id
            informer.dynamic = False
            if not isManager:
                informer.user_login = user
            informer.admaker = object.get('options')
            informer.css = None
            informer.css_banner = None
            informer.title = object.get('title')
            if object.get('domain'):
                informer.domain = object.get('domain')
            informer.non_relevant = object.get('nonRelevant')
            informer.height = object.get('height')
            informer.width = object.get('width')
            informer.height_banner = object.get('height_banner')
            informer.width_banner = object.get('width_banner')
            if object.get('html_notification'):
                informer.html_notification = object.get('html_notification')
            if object.get('plase_branch'):
                informer.plase_branch = object.get('plase_branch')
            if object.get('retargeting_branch'):
                informer.retargeting_branch = object.get('retargeting_branch')
            informer.auto_reload = object.get('auto_reload', 0)
            if object.get('blinking'):
                informer.blinking = object.get('blinking', 0)
            if object.get('shake'):
                informer.shake = object.get('shake', 0)
            if object.get('rating_division'):
                informer.rating_division = object.get('rating_division', 1000)
            if object.get('blinking_reload'):
                informer.blinking_reload = object.get('blinking_reload')
            if object.get('shake_reload'):
                informer.shake_reload = object.get('shake_reload')
            if object.get('shake_mouse'):
                informer.shake_mouse = object.get('shake_mouse')
            informer.save()
            return h.JSON({'error': False, 'id': informer.guid})
        except Exception as ex:
            log.debug("Error in advertise.save(): " + str(ex))
            return h.JSON({'error': True, 'id': informer.guid,
                           'message': unicode(ex)})

    def save_dynamic(self):
        try:
            user = session.get('user')
            isManager = session.get('isManager', False)
            if not user:
                return h.JSON({'error': True, 'message': u'Не выполнен вход'})
            id = request.params.get('adv_id')
            object = json.loads(request.body)
            informer = model.Informer()
            informer.loadGuid(id)
            informer.guid = id
            informer.dynamic = True
            if not isManager:
                informer.user_login = user
            informer.admaker = object.get('options')
            informer.non_relevant = object.get('nonRelevant')
            informer.css = ' '
            informer.css_banner = ' '
            informer.title = object.get('title')
            if object.get('domain'):
                informer.domain = object.get('domain')
            informer.height = 1
            informer.width = 1
            informer.height_banner = 1
            informer.width_banner = 1
            informer.html_notification = True
            informer.plase_branch = True
            informer.retargeting_branch = True
            informer.auto_reload = 0
            informer.blinking = 0
            informer.shake = 0
            informer.rating_division = 1000
            informer.blinking_reload = False
            informer.shake_reload = False
            informer.shake_mouse = False
            informer.save()
            return h.JSON({'error': False, 'id': informer.guid})
        except Exception as ex:
            log.debug("Error in advertise.save(): " + str(ex))
            return h.JSON({'error': True, 'id': informer.guid,
                           'message': unicode(ex)})

    def pattern_save(self):
        try:
            user = session.get('user')
            if not user:
                return h.JSON({'error': True, 'message': u'Не выполнен вход'})
            id = request.params.get('adv_id')
            object = json.loads(request.body)
            informer = model.InformerPattern()
            informer.guid = id
            informer.admaker = object.get('options')
            informer.save()
            return h.JSON({'error': False, 'id': informer.guid})
        except Exception as ex:
            log.debug("Error in advertise.save(): " + str(ex))
            return h.JSON({'error': True, 'id': informer.guid,
                           'message': unicode(ex)})

    def showList(self):
        user = session.get('user')
        if not user:
            return "Login!"
        advertises = app_globals.db.informer.find({'dynamic': {'$ne': True}}).sort('user')
        data = [{'title': x['title'],
                 'guid': x['guid'],
                 'domain': x['domain'],
                 'lastModified': x['lastModified'],
                 'user': x['user']
                 } for x in advertises]
        return render('/advertiseList.mako.html', extra_vars={'data': data})

    def patternList(self):
        user = session.get('user')
        if not user:
            return "Login!"
        advertises = app_globals.db.informer.patterns.find().sort('popular', -1)
        data = [{'title': x['title'],
                 'guid': x['guid'],
                 'popular': x['popular'],
                 'orient': x['orient'],
                 } for x in advertises]
        return render('/patternList.mako.html', extra_vars={'data': data})

    def days(self, json=True):
        """ Возвращает разбитые по дням клики для каждой выгрузки текущего
            пользователя (для графиков).

            Формат: [{adv: {
                        guid: '...',
                        title: '...'
                      },
                      data: [[datestamp, clicks], [datestamp, clicks], ...],
                ...]
        """
        user = session.get('user')
        if not user:
            return ""

        result = []
        data = model.StatisticReport().statAdvByDate(user)
        for item in data:
            temp = {}
            for tmp in item['data']:
                temp[tmp[0]] = temp.get(tmp[0], 0.0) + tmp[1]
            dateclick = [(int(time.mktime(key.timetuple()) * 1000), value) for key, value in temp.items()]
            dateclick.sort(key=lambda x: x[0])
            result.append({'adv': {'guid': item['guid'],
                                   'title': item['title'],
                                   'domain': item['domain']},
                           'data': dateclick
                           })

        return h.JSON(result) if json else result

    def domainsAdvertises(self):
        """ Возвращает выгрузки относящиеся к домену """
        user = session.get('user')
        domain = request.params.get('domain')
        advertises = self._domainsAdvertises(domain)

        return h.jgridDataWrapper(advertises)

    def _domainsAdvertises(self, domain):
        """ Возвращает выгрузки относящиеся к домену """
        if domain:
            advertises = [(x['title'], x['guid'], x.get('dynamic', False))
                          for x in app_globals.db.informer.find({
                    'user': session.get('user'),
                    'domain': domain})]
        else:
            advertises = [(x['title'], x['guid'], x.get('dynamic', False))
                          for x in app_globals.db.informer.find({
                    'user': session.get('user'),
                    'domain': {'$exists': False}})]
        return advertises

    def daysSummary(self):
        """Возвращает данные для таблицы суммарной статистики по дням """
        user = session.get('user')
        dateStart = dateFromStr(request.params.get('dateStart', None))
        dateEnd = dateFromStr(request.params.get('dateEnd', None))
        adv = request.params.get('adv')
        if user:
            from math import ceil
            try:
                page = int(request.params.get('page'))
                rows = int(request.params.get('rows'))
            except:
                page = 1
                rows = 10
            if not adv:
                data = model.StatisticReport().statUserGroupedByDate(
                    user, dateStart, dateEnd)
            else:
                data = model.StatisticReport().statAdvGroupedByDate(
                    adv, dateStart, dateEnd)
            data.sort(key=lambda x: x['date'])
            data.reverse()
            totalPages = int(ceil(float(len(data)) / rows))
            data = data[(page - 1) * rows: page * rows]
            data = [{'id': index,
                     'cell': (
                         "<b>%s</b>" % x['date'].strftime("%d.%m.%Y"),
                         x['impressions_block_not_valid'],
                         x['impressions_block'],
                         x['unique'],
                         '%.3f%%' %
                         (round(x['unique'] * 100 / x['impressions_block'], 3)
                          if x['impressions_block'] else 0),
                         '%.2f грн' %
                         ((round(x['summ'] / x['unique'], 3)
                           if x['unique'] > 0 else 0)),
                         '%.2f грн' % x['summ']
                     )
                     }
                    for index, x in enumerate(data)]
            return json.dumps({'total': totalPages,
                               'page': page,
                               'records': len(data),
                               'rows': data
                               },
                              default=bson.json_util.default,
                              ensure_ascii=False)
        else:
            return ""

    def allAdvertises(self, json=True):
        """ Суммарный отчёт по всем рекламным площадкам """
        user = session.get('user')
        dateStart = dateFromStr(request.params.get('dateStart', None))
        dateEnd = dateFromStr(request.params.get('dateEnd', None))

        reportData = model.StatisticReport().allAdvertiseScriptsSummary(user, dateStart, dateEnd)
        reportData.sort(cmp=lambda x, y: cmp(x['advTitle'], y['advTitle']),
                        key=None, reverse=False)
        data = [{'id': r['adv'],
                 'cell': [
                     r['advTitle'],
                     r['impressions_block_not_valid'],
                     r['impressions_block'],
                     r['unique'],
                     '%.3f%%' % round(r['unique'] * 100.0 / r['impressions_block'], 3)
                     if r['impressions_block'] else 0,
                     '%.2f грн' %
                     ((round(r['totalCost'] / r['unique'], 3)
                       if r['unique'] > 0 else 0)),
                     '%.2f грн' % round(r['totalCost'], 2)
                 ]}
                for index, r in enumerate(reportData)]

        totalImpressions = sum([r['impressions_block'] for r in reportData if 'impressions_block' in r])

        impressions_block_not_valid = sum(
            [r['impressions_block_not_valid'] for r in reportData if 'impressions_block_not_valid' in r])

        totalUnique = sum([r['unique'] for r in reportData if 'unique' in r])

        totalCost = sum([r['totalCost'] for r in reportData if 'totalCost' in r])

        result = {
            'total': len(data),
            'page': 1,
            'records': len(data),
            'rows': data,
            'userdata': {
                "Title": u"ИТОГО",
                "Impressions": impressions_block_not_valid,
                "ImpressionsValid": totalImpressions,
                "Clicks": totalUnique,
                "CTR": '%.3f%%' % round(totalUnique * 100.0 / totalImpressions, 3) if totalImpressions else 0,
                "Cost": '%.2f грн' % (round(totalCost / totalUnique, 3) if totalUnique > 0 else 0),
                "Summ": '%.2f грн' % totalCost
            }}

        return h.JSON(result) if json else result

    def create(self):
        """Создание выгрузки"""
        user = session.get('user')
        if not user:
            redirect(url_for(controller='main', action='index'))
        c.patterns = self._patterns()
        c.advertise = None
        c.domains = model.Account(login=user).domains()
        return render("/create_adv.mako.html")

    def create_dynamic(self):
        """Создание выгрузки"""
        user = session.get('user')
        if not user:
            redirect(url_for(controller='main', action='index'))
        c.patterns = self._patterns()
        c.advertise = None
        c.domains = model.Account(login=user).domains()
        return render("/create_adv_dynamic.mako.html")

    def edit(self):
        """Редактирование выгрузки"""
        user = session.get('user')
        if not user:
            redirect(url_for(controller='main', action='index'))
        guid = request.params.get('ads_id')
        x = app_globals.db.informer.find_one({'guid': guid})
        if not x:
            return u"Информер не найден!"

        advertise = {'title': x['title'],
                     'guid': x['guid'],
                     'options': x['admaker'],
                     'domain': x.get('domain', ''),
                     'auto_reload': x.get('auto_reload', 0),
                     'blinking': x.get('blinking', 0),
                     'shake': x.get('shake', 0),
                     'rating_division': x.get('rating_division', 1000),
                     'non_relevant': x.get('nonRelevant', {}),
                     'html_notification': bool(x.get('html_notification', False)),
                     'blinking_reload': bool(x.get('blinking_reload', False)),
                     'shake_reload': bool(x.get('shake_reload', False)),
                     'shake_mouse': bool(x.get('shake_mouse', False))
                     }

        advertise['non_relevant']['userCode'] = escape(advertise['non_relevant'].get('userCode', ''))
        c.patterns = self._patterns()
        c.advertise = advertise
        c.domains = model.Account(login=user).domains()
        return render("/create_adv.mako.html")

    def edit_dynamic(self):
        """Редактирование выгрузки"""
        user = session.get('user')
        if not user:
            redirect(url_for(controller='main', action='index'))
        guid = request.params.get('ads_id')
        x = app_globals.db.informer.find_one({'guid': guid})
        if not x:
            return u"Информер не найден!"

        advertise = {'title': x['title'],
                     'guid': x['guid'],
                     'options': x.get('admaker', {}),
                     'domain': x.get('domain', ''),
                     'auto_reload': x.get('auto_reload', 0),
                     'blinking': x.get('blinking', 0),
                     'shake': x.get('shake', 0),
                     'rating_division': x.get('rating_division', 1000),
                     'non_relevant': x.get('nonRelevant', {}),
                     'html_notification': bool(x.get('html_notification', False)),
                     'blinking_reload': bool(x.get('blinking_reload', False)),
                     'shake_reload': bool(x.get('shake_reload', False)),
                     'shake_mouse': bool(x.get('shake_mouse', False))
                     }

        advertise['non_relevant']['userCode'] = escape(advertise['non_relevant'].get('userCode', ''))
        c.patterns = self._patterns()
        c.advertise = advertise
        c.domains = model.Account(login=user).domains()
        return render("/create_adv_dynamic.mako.html")

    def _patterns(self):
        """Возвращает образцы выгрузок"""
        return [{'title': x['title'],
                 'guid': x['guid'],
                 'options': x['admaker'],
                 'orient': x.get('orient'),
                 'popular': x.get('popular'),
                 'height': x.get('height'),
                 'width': x.get('width'),
                 'auto_reload': x.get('auto_reload', 0),
                 'height_banner': x.get('height_baner'),
                 'width_banner': x.get('width_baner'), }
                for x in app_globals.db.informer.patterns.find({}).sort('title')]

    def remove(self):
        """Удаляет выгрузки"""
        try:
            user = session.get('user')
            if not user:
                redirect(url_for(controller='main', action='index'))
            guid = request.params.get('ads_id')
            app_globals.db.informer.remove({'guid': guid})
        except Exception as e:
            return h.JSON({'error': True, 'msg': e})
        else:
            return h.JSON({'error': False})
