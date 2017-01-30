# This file uses following encoding: utf-8
from amqplib import client_0_8 as amqp
from getmyad.lib.base import render
from getmyad.model.Campaign import Campaign
from getmyad.model.Offer import Offer
from getmyad.model import mq
from pylons import request, response, session, tmpl_context as c, url, \
    app_globals, config
from pylons.controllers import XMLRPCController
from pylons.controllers.util import abort, redirect
from pylons.decorators.cache import beaker_cache
from uuid import uuid1
from getmyad.lib.adload_data import AdloadData
from PIL import Image
import StringIO
import datetime
import ftplib
import logging
import urllib
from getmyad.tasks.mail import campaign_offer_update
import datetime

log = logging.getLogger(__name__)


class RpcController(XMLRPCController):
    ''' Предоставляет XML-RPC интерфейс управления и взаимодействия с GetMyAd '''

    def server_status(self):
        ' Состояние сервера и некоторая статистика GetMyAd'
        res = {'ok': True,
               'camapaigns': app_globals.db_m.campaign.find().count(),
               'offers': app_globals.db_m.offer.find().count()}
        return res

    server_status.signature = [['struct']]

    def campaign_start(self, campaign_id):
        """ Запуск рекламной кампании ``campaign_id`` в GetMyAd.
        
        У кампании должно быть разрешение рекламу в GetMyAd *(см. методы AdLoad API
        campaign.addToGetMyAd и campaign.removeFromGetmyad)*.
        
        Для получения всей информации метод обращается к AdLoad. В процессе работы создаётся
        кампания и загружаются её рекламные предложения. Если кампания уже была запущена ранее,
        а затем остановлена, настройки её будут восстановлены из архива (коллеция 
        ``campaign.arhive``).
        
        Если кампания уже запущена, метод вернёт сообщение об этом и ничего не сделает.
        """
        campaign_id = campaign_id.lower()
        camp = Campaign(campaign_id)
        camp.project = 'adload'
        print camp.is_hold()
        if not camp.exists():
            if not camp.restore_from_archive():
                camp.save()  # Сохраняем пустую кампанию
        camp.load()
        camp.started()
        return self.campaign_update(campaign_id)

    campaign_start.signature = [['string', 'string']]

    def campaign_stop(self, campaign_id):
        ''' Остановка рекламной кампании ``campaign_id`` в GetMyAd '''
        campaign_id = campaign_id.lower()
        camp = Campaign(campaign_id)
        camp.stop()
        app_globals.db_m.offer.remove({'campaignId': campaign_id}, safe=True)
        app_globals.db_m.stats_daily.rating.remove({'campaignId': campaign_id}, safe=True)
        camp.move_to_archive()
        mq.MQ().campaign_stop(campaign_id)  # Отправляем сообщение 
        return "ok"

    campaign_stop.signature = [['string', 'string']]

    def campaign_work(self, campaign_id):
        '''Заморозка рекламной кампании ``campaign_id`` в GetMyAd '''
        campaign_id = campaign_id.lower()
        camp = Campaign(campaign_id)
        camp.working()
        mq.MQ().campaign_update(campaign_id)  # Отправляем сообщение 
        return "ok"

    campaign_work.signature = [['string', 'string']]

    def campaign_hold(self, campaign_id):
        '''Заморозка рекламной кампании ``campaign_id`` в GetMyAd '''
        campaign_id = campaign_id.lower()
        camp = Campaign(campaign_id)
        camp.hold()
        mq.MQ().campaign_stop(campaign_id)  # Отправляем сообщение 
        return "ok"

    campaign_hold.signature = [['string', 'string']]

    def campaign_update(self, campaign_id):
        ''' Обновляет рекламную кампанию ``campaign_id``.
        
        При обновлении происходит получение от AdLoad нового списка предложений и
        общей информации о кампании.
        
        Если кампания не была запущена, ничего не произойдёт.
        
        Если в кампании нет активных предложений, она будет остановлена.
        '''
        a = datetime.datetime.now()
        campaign_id = campaign_id.lower()
        camp = Campaign(campaign_id)

        try:
            camp.load()
        except Campaign.NotFoundError:
            return 'Campaign is not running'

        ad = AdloadData()
        details = ad.campaign_details(campaign_id)

        # Если кампании уже нет в AdLoad или она помечена как запрещённая для показа в getmyad,
        # останавливаем её в GetMyAd
        if not details or not details.get('getmyad'):
            result_stop = self.campaign_hold(campaign_id)
            return u"Кампания не запущена в AdLoad или запрещена для показа в GetMyAd. \n" + \
                   u"Останавливаю кампанию: %s" % result_stop

        camp.title = details['title']
        camp.last_update = datetime.datetime.now()
        camp.project = 'adload'
        camp.account = details['account']
        camp.manager = details.get('manager', '')
        camp.update_status = 'initial'
        camp.save()
        count = ad.offer_count(campaign_id)

        if count < 1:
            # Если у кампании нет товарных предложний, это скорее всего значит,
            # что на счету закончились деньги
            result_stop = self.campaign_hold(campaign_id)
            camp.update_status = 'complite'
            camp.save()
            return u"В кампании нет активных предложений. \n" + \
                   u"Возможные причины: на счету кампании нет денег, не отработал парсер Рынка (для интернет-магазинов).\n" + \
                   u"Замораживаю кампанию: %s" % result_stop

        campaign_offer_update.delay(campaign_id)
        # campaign_offer_update(campaign_id)
        return 'ok'

    campaign_update.signature = [['string', 'string']]

    def campaign_list(self):
        ''' Возвращает список всех запущенных в GetMyAd кампаний.
        '''  # TODO: Дописать документацию

        result = []
        for x in app_globals.db_m.campaign.find({"project": "adload"}):
            campaign = {'id': x.get('guid'),
                        'title': x.get('title')}
            result.append(campaign)
        return result

    campaign_list.signature = [['array']]

    def campaign_details(self, campaign_id):
        ''' Возвращает состояние кампании ``campaign_id``.
        
        Ответ имеет следующий формат::
        
            (struct)
                'id': (string)
                'title': (string)
                'status': (string)
                'offersCount': (int)
                'lastUpdate': (datetime)
            (struct-end)
        
        
        Поля ``id``и ``title`` обозначают id и наименование кампании соответственно.
        Количество запущенных предложений находится в ``offersCount``. Время последней
        синхронизации с AdLoad --- ``lastUpdate``.
         
        Поле ``status`` обозначает состояние кампании и может принимать следующие значения:
        
        +---------------+---------------------------------------------------------------+
        |     status    |  Описание                                                     | 
        +===============+===============================================================+
        | ``not_found`` |  Кампания не была запущена в GetMyAd, либо такой кампании не  |
        |               |  существует в принципе. Вернутся только поля ``id`` и         |
        |               |  ``status``.                                                  |
        +---------------+---------------------------------------------------------------+
        |  ``working``  |  Кампания запущена и работает в данный момент.                |
        |               |                                                               |
        +---------------+---------------------------------------------------------------+
         
        '''
        campaign_id = campaign_id.lower()
        c = Campaign(campaign_id)
        if not c.exists():
            return {'status': c.status}
        c.load()
        offers_count = app_globals.db_m.offer.find({'campaignId': campaign_id}).count()
        offers_count_image = app_globals.db_m.offer.find({'campaignId': campaign_id, 'image': {'$ne': ''}}).count()
        return {'id': c.id,
                'title': c.title,
                'status': c.status,
                'offersCount': offers_count,
                'offersCountImage': offers_count_image,
                'update': c.is_update(),
                'lastUpdate': c.last_update
                }

    def maintenance_uploadEmergencyAds(self):
        ''' Загружает аварийные заглушки для всех информеров '''
        from getmyad.model import InformerFtpUploader
        uploaded_count = 0
        failed_count = 0
        for i in app_globals.db.informer.find({}, fields=['guid']):
            try:
                InformerFtpUploader(i['guid']).upload_reserve()
                uploaded_count += 1
            except:
                failed_count += 1
        return {'uploaded_informers': uploaded_count, 'failed': failed_count}

    def maintenance_uploadInformerLoaders(self):
        ''' Загружает javascript загрузчики для всех информеров '''
        from getmyad.model import InformerFtpUploader
        uploaded_count = 0
        failed_count = 0
        for i in app_globals.db.informer.find({}, fields=['guid']):
            try:
                InformerFtpUploader(i['guid']).upload_loader()
                uploaded_count += 1
            except:
                failed_count += 1
        return {'uploaded_informers': uploaded_count, 'failed': failed_count}
