# -*- coding: UTF-8 -*-
import datetime
from getmyad.lib.helpers import uuid_to_long

from pylons import app_globals


class Campaign(object):
    "Класс описывает рекламную кампанию, запущенную в GetMyAd"

    class NotFoundError(Exception):
        'Кампания не найдена'

        def __init__(self, id, db=None):
            self.id = id
            if db is None:
                self.db = app_globals.db_m
            else:
                self.db = db

    def __init__(self, id, db=None):
        if db is None:
            self.db = app_globals.db_m
        else:
            self.db = db
        #: ID кампании
        self.id = id.lower()
        self.id_int = uuid_to_long(self.id.encode('utf-8'))
        #: Заголовок рекламной кампании
        self.title = ''
        #: Является ли кампания социальной рекламой
        self.social = False
        #: Является ли кампания социальной рекламой
        self.project = ''
        self.account = ''
        self.manager = ''
        self.target = ''
        # Настройки отображения
        self.disabled_retargiting_style = False
        self.disabled_recomendet_style = False
        #: Добавлять ли к ссылкам предложений маркер yottos_partner=...
        self.yottos_partner_marker = True
        self.yottos_translit_marker = False
        self.yottos_hide_site_marker = False
        #: Время последнего обновления (см. rpc/campaign.update())
        self.last_update = datetime.datetime.now()
        #: Уникальность
        self.UnicImpressionLot = 1
        #: Тлько контекст, временное решение
        self.thematic = False
        self.retargeting = False
        self.brending = False
        self.style_type = 'default'
        self.style_data = {}
        self.html_notification = False
        self.offer_by_campaign_unique = 1
        self.load_count = 100
        self.status = 'created'
        self.day_of_holden = None
        self.update_status = 'complite'
        if self.exists():
            self.load()

    def load(self):
        'Загружает кампанию из базы данных'
        c = self.db.campaign.find_one({'guid': self.id})
        if not c:
            raise Campaign.NotFoundError(self.id, self.db)
        self.id = c.get('guid')
        self.id_int = c.get('guid_int', uuid_to_long(self.id.encode('utf-8')))
        self.title = c.get('title')
        self.account = c.get('account')
        self.manager = c.get('manager')
        self.social = c.get('social', False)
        self.project = c.get('project', '')
        self.disabled_retargiting_style = c.get('disabled_retargiting_style', False)
        self.disabled_recomendet_style = c.get('disabled_recomendet_style', False)
        self.yottos_partner_marker = c.get('yottosPartnerMarker', True)
        self.yottos_translit_marker = c.get('yottosTranslitMarker', False)
        self.yottos_hide_site_marker = c.get('yottosHideSiteMarker', False)
        self.status = c.get('status', 'working')
        self.last_update = c.get('lastUpdate', datetime.datetime.now())
        self.day_of_holden = c.get('day_of_holden')
        self.update_status = c.get('update_status', 'complite')
        if c.has_key('showConditions'):
            self.offer_by_campaign_unique = c['showConditions'].get('offer_by_campaign_unique', 1)
            self.UnicImpressionLot = c['showConditions'].get('UnicImpressionLot', 1)
            self.load_count = c['showConditions'].get('load_count', 100)
            self.thematic = c['showConditions'].get('thematic', False)
            self.retargeting = c['showConditions'].get('retargeting', False)
            self.html_notification = c['showConditions'].get('html_notification', False)
            self.target = c['showConditions'].get('target', '')
            self.brending = c['showConditions'].get('brending', False)
            self.style_type = c['showConditions'].get('style_type', 'default')
            self.style_data = c['showConditions'].get('style_data', {})
        else:
            self.offer_by_campaign_unique = 1
            self.UnicImpressionLot = 1
            self.load_count = 100
            self.thematic = False
            self.retargeting = False
            self.html_notification = False
            self.target = ''
            self.brending = False
            self.style_type = 'default'
            self.style_data = {}

    def restore_from_archive(self):
        'Пытается восстановить кампанию из архива. Возвращает true в случае успеха'
        c = self.db.campaign.archive.find_one({'guid': self.id})
        if not c:
            return False
        self.delete()
        self.db.campaign.save(c)
        self.db.campaign.archive.remove({'guid': self.id})

        return True

    def save(self):
        'Сохраняет кампанию в базу данных'
        self.db.campaign.update(
            {'guid': self.id},
            {'$set': {'guid_int': self.id_int,
                      'title': self.title,
                      'social': self.social,
                      'project': self.project,
                      'account': self.account,
                      'manager': self.manager,
                      'disabled_retargiting_style': self.disabled_retargiting_style,
                      'disabled_recomendet_style': self.disabled_recomendet_style,
                      'yottosPartnerMarker': self.yottos_partner_marker,
                      'yottosTranslitMarker': self.yottos_translit_marker,
                      'yottosHideSiteMarker': self.yottos_hide_site_marker,
                      'offer_by_campaign_unique': self.offer_by_campaign_unique,
                      'load_count': self.load_count,
                      'lastUpdate': self.last_update,
                      'day_of_holden': self.day_of_holden,
                      'update_status': self.update_status,
                      'status': self.status}},
            upsert=True)

    def exists(self):
        'Возвращает ``True``, если кампания с заданным ``id`` существует'
        return self.db.campaign.find_one({'guid': self.id}) is not None

    def is_created(self):
        return self.status == 'created'

    def is_started(self):
        return self.status == 'started'

    def started(self):
        self.status = 'started'
        self.save()

    def is_configured(self):
        return self.status == 'configured'

    def configured(self):
        self.status = 'configured'
        self.save()

    def hold(self):
        self.status = 'hold'
        self.save()

    def is_hold(self):
        return self.status == 'hold'

    def working(self):
        self.status = 'working'
        self.save()

    def is_working(self):
        return self.status == 'working'

    def is_update(self):
        return (self.update_status != 'complite' and (self.last_update + datetime.timedelta(minutes=3)) >= (
            datetime.datetime.now() - datetime.timedelta(minutes=33)))

    def is_stop(self):
        return self.status == 'stop'

    def stop(self):
        self.status = 'stop'
        self.save()

    def delete(self):
        'Удаляет кампанию'
        self.db.campaign.remove({'guid': self.id})

    def move_to_archive(self):
        'Перемещает кампанию в архив'
        c = self.db.campaign.find_one({'guid': self.id})
        if not c: return
        self.db.campaign.archive.remove({'guid': self.id})
        self.db.campaign.archive.save(c)
        self.delete()

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setattr__(self, name, value):
        if name == 'status':
            if value == 'hold':
                if self.day_of_holden is None:
                    super(Campaign, self).__setattr__('day_of_holden', datetime.datetime.now())
            else:
                super(Campaign, self).__setattr__('day_of_holden', None)
        super(Campaign, self).__setattr__(name, value)