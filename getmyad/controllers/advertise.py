# -*- coding: utf-8 -*-
# This Python file uses the following encoding: utf-8
from datetime import datetime
from getmyad.lib.base import BaseController, render
from getmyad.model import StatisticReports
from pylons import request, response, session, tmpl_context as c, url, app_globals, config
from pylons.controllers.util import abort, redirect
from routes.util import url_for
import getmyad.lib.helpers as h
import getmyad.model as model
import json
import logging
import bson.json_util
import re
import time
from pprint import pprint

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
        from webhelpers.html.builder import escape
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
            if not user:
                return h.JSON({'error': True, 'message': u'Не выполнен вход'})
            id = request.params.get('adv_id')
            object = json.loads(request.body)
            informer = model.Informer()
            informer.loadGuid(id)
            informer.guid = id
            informer.user_login = user
            informer.admaker = object.get('options')
            informer.css = None
            informer.css_banner = None
            informer.title = object.get('title')
            informer.domain = object.get('domain')
            informer.non_relevant = object.get('nonRelevant')
            informer.height = object.get('height')
            informer.width = object.get('width')
            informer.height_banner = object.get('height_banner')
            informer.width_banner = object.get('width_banner')
            if object.get('html_notification') is not None:
                informer.html_notification = object.get('html_notification')
            if object.get('plase_branch') is not None:
                informer.plase_branch = object.get('plase_branch')
            if object.get('retargeting_branch') is not None:
                informer.retargeting_branch = object.get('retargeting_branch')
            informer.auto_reload = object.get('auto_reload', 0)
            if object.get('blinking') is not None:
                informer.blinking = object.get('blinking', 0)
            if object.get('shake') is not None:
                informer.shake = object.get('shake', 0)
            if object.get('rating_division') is not None:
                informer.rating_division = object.get('rating_division', 1000)
            if object.get('blinking_reload') is not None:
                informer.blinking_reload = object.get('blinking_reload')
            if object.get('shake_reload') is not None:
                informer.shake_reload = object.get('shake_reload')
            if object.get('shake_mouse') is not None:
                informer.shake_mouse = object.get('shake_mouse')
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
        advertises = app_globals.db.informer.find().sort('user')
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
            advertises = [(x['title'], x['guid'])
                          for x in app_globals.db.informer.find({
                    'user': session.get('user'),
                    'domain': domain})]
        else:
            advertises = [(x['title'], x['guid'])
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
                         x['unique'],
                         '%.3f%%' %
                         (round(x['unique'] * 100 / x['impressions_block_not_valid'], 3)
                          if x['impressions_block_not_valid'] else 0),
                         '%.3f%%' % x['difference_impressions_block'],
                         h.secontToString((float(x['view_seconds']) / (x['clicks'] + x['social_clicks']) if (
                             (x['clicks'] + x['social_clicks']) > 0) else 0), "{m}m : {s}s"),
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
                     r['unique'],
                     '%.3f%%' % round(r['unique'] * 100 / r['impressions_block_not_valid'], 3)
                     if r['impressions_block_not_valid'] else 0,
                     '%.3f%%' % r['difference_impressions_block'],
                     h.secontToString((float(r['view_seconds']) / (r['clicks'] + r['social_clicks']) if (
                         (r['clicks'] + r['social_clicks']) > 0) else 0), "{m}m : {s}s"),
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
        view_seconds = sum([r['view_seconds'] for r in reportData if 'view_seconds' in r])
        clicks = sum([r['clicks'] for r in reportData if 'clicks' in r])
        social_clicks = sum([r['social_clicks'] for r in reportData if 'social_clicks' in r])

        result = {
            'total': len(data),
            'page': 1,
            'records': len(data),
            'rows': data,
            'userdata': {
                "Title": u"ИТОГО",
                "Impressions": impressions_block_not_valid,
                "Clicks": totalUnique,
                "CTR": '%.3f%%' % \
                       round(totalUnique * 100 / impressions_block_not_valid, 3) \
                    if impressions_block_not_valid else 0,
                "ViewPort": '%.3f%%' % \
                            (round(100.0 * totalImpressions / impressions_block_not_valid, 3) \
                                 if impressions_block_not_valid > totalImpressions else 100),
                "ViewSecond": h.secontToString(
                    view_seconds / (clicks + social_clicks) if ((clicks + social_clicks) > 0) else 0, "{m}m : {s}s"),
                "Cost": '%.2f грн' % \
                        (round(totalCost / totalUnique, 3) \
                             if totalUnique > 0 else 0),
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
        from webhelpers.html.builder import escape
        advertise['non_relevant']['userCode'] = escape(advertise['non_relevant'].get('userCode', ''))
        c.patterns = self._patterns()
        c.advertise = advertise
        c.domains = model.Account(login=user).domains()
        return render("/create_adv.mako.html")

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
            raise
            return h.JSON({'error': True, 'msg': e})
        else:
            return h.JSON({'error': False})
