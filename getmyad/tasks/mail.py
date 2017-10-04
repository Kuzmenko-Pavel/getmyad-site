# -*- coding: utf-8 -*-

from uuid import uuid1
import cStringIO
import ftplib
import urllib2
import datetime
import pymssql

import letter
from letter import Letter
from celery.task import task
from PIL import Image
import os
import pymongo
from amqplib import client_0_8 as amqp

GETMYAD_XMLRPC_HOST = 'https://getmyad.yottos.com/rpc'
MONGO_HOST = 'srv-5.yottos.com:27018,srv-5.yottos.com:27020,srv-5.yottos.com:27019'
MONGO_DATABASE = 'getmyad_db'
otype = type

# Параметры FTP для заливки статических файлов на сервер CDN
cdn_server_url = 'https://cdn.yottos.com/'
cdn_ftp = 'srv-3.yottos.com'
cdn_ftp_list = ['srv-3.yottos.com', 'srv-6.yottos.com', 'srv-7.yottos.com', 'srv-8.yottos.com', 'srv-9.yottos.com']
cdn_ftp_user = 'cdn'
cdn_ftp_password = '$www-app$'
cdn_ftp_path = 'httpdocs'


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


def _get_worker_channel():
    ''' Подключается к брокеру mq '''
    conn = amqp.Connection(host='srv-4.yottos.com',
                           userid='worker',
                           password='worker',
                           virtual_host='worker',
                           insist=True)
    ch = conn.channel()
    ch.exchange_declare(exchange="getmyad", type="topic", durable=True, auto_delete=False, passive=False)
    return ch


def campaign_update(campaign_id):
    ''' Отправляет уведомление об обновлении рекламной кампании ``campaign_id`` '''
    ch_worker = _get_worker_channel()
    msg = amqp.Message(campaign_id)
    ch_worker.basic_publish(msg, exchange='getmyad', routing_key='campaign.update')
    ch_worker.close()
    print "AMQP campaign_update", campaign_id


def campaign_stop(campaign_id):
    ''' Отправляет уведомление об обновлении рекламной кампании ``campaign_id`` '''
    ch_worker = _get_worker_channel()
    msg = amqp.Message(campaign_id)
    ch_worker.basic_publish(msg, exchange='getmyad', routing_key='campaign.stop')
    ch_worker.close()
    print "AMQP campaign_stop", campaign_id


def account_update(login):
    ''' Отправляет уведомление об изменении в аккаунте ``login`` '''
    ch_worker = _get_worker_channel()
    msg = amqp.Message(login)
    ch_worker.basic_publish(msg, exchange='getmyad', routing_key='account.update')
    ch_worker.close()
    try:
        print "AMQP Account update %s" % login
    except Exception as e:
        print e


def mssql_connection_adload():
    """

    Returns:

    """
    pymssql.set_max_connections(450)
    conn = pymssql.connect(host='srv-1.yottos.com',
                           user='web',
                           password='odif8duuisdofj',
                           database='1gb_YottosAdLoad',
                           as_dict=True,
                           charset='cp1251')
    conn.autocommit(True)
    return conn


try:
    from pylons import config

    letter.TEMPLATES_DIRS = [os.path.join(config['pylons.paths']['templates'][0], 'mail')]
except Exception:
    current_dir = os.path.dirname(__file__)
    letter.TEMPLATES_DIRS = [os.path.join(current_dir, '../templates/mail')]


@task(max_retries=10, default_retry_delay=10)
def registration_request_manager(**kwargs):
    """

    Args:
        kwargs:
    """
    email = 'Elena@yottos.com'
    try:
        letter = Letter()
        letter.sender = 'support@yottos.com'
        letter.sender_name = 'Yottos GetMyAd'
        letter.recipients = email
        letter.subject = u'Заявка на регистрацию в GetMyAd'
        letter.template = 'managers/registration_request.mako.txt'
        letter.set_message(**kwargs)
        letter.send('mail.yottos.com', 25, 'support@yottos.com', '57fd8824')
    except Exception as ex:
        print "sendmail failed to %s: %s (retry #%s)" % (email, ex, kwargs.get('task_retries', 0))
        registration_request_manager.retry(args=[], kwargs=kwargs, exc=ex)
    else:
        print "sendmail to %s ok" % email


@task(max_retries=10, default_retry_delay=10)
def registration_request_user(email, **kwargs):
    """

    Args:
        email:
        kwargs:
    """
    try:
        letter = Letter()
        letter.sender = 'support@yottos.com'
        letter.sender_name = 'Yottos GetMyAd'
        letter.recipients = email
        letter.subject = u'Рекламная сеть Yottos - заявка на участие сайта %s' % kwargs['site_url']
        letter.template = 'users/registration_request.mako.txt'
        letter.set_message(**kwargs)
        letter.send('mail.yottos.com', 25, 'support@yottos.com', '57fd8824')
    except Exception as ex:
        print "sendmail failed to %s: %s (retry #%s)" % (email, ex, kwargs.get('task_retries', 0))
        registration_request_user.retry(args=[email], kwargs=kwargs, exc=ex)
    else:
        print "sendmail to %s ok" % email


@task(max_retries=10, default_retry_delay=10)
def money_out_request(payment_type, email, **kwargs):
    """

    Args:
        payment_type:
        email:
        kwargs:
    """
    try:
        letter = Letter()
        letter.sender = 'support@yottos.com'
        letter.sender_name = 'Yottos GetMyAd'
        letter.recipients = email
        letter.subject = u'Вывод средств Yottos GetMyAd'
        if payment_type == 'webmoney_z':
            letter.template = 'users/money_out/webmoney.mako.txt'
        elif payment_type == 'webmoney_r':
            letter.template = 'users/money_out/webmoney.mako.txt'
        elif payment_type == 'webmoney_u':
            letter.template = 'users/money_out/webmoney.mako.txt'
        elif payment_type == 'cash':
            letter.template = 'users/money_out/cash.mako.txt'
        elif payment_type == 'card':
            letter.template = 'users/money_out/card.mako.txt'
        elif payment_type == 'card_pb_ua':
            letter.template = 'users/money_out/card_pb_ua.mako.txt'
        elif payment_type == 'card_pb_us':
            letter.template = 'users/money_out/card_pb_us.mako.txt'
        elif payment_type == 'factura':
            letter.template = 'users/money_out/invoice.mako.txt'
        elif payment_type == 'yandex':
            letter.template = 'users/money_out/yandex.mako.txt'

        letter.set_message(**kwargs)
        letter.send('mail.yottos.com', 25, 'support@yottos.com', '57fd8824')
    except Exception as ex:
        print "sendmail failed to %s: %s (retry #%s)" % (email, ex, kwargs.get('task_retries', 0))
        money_out_request.retry(args=[payment_type, email], kwargs=kwargs, exc=ex)
    else:
        print "sendmail to %s ok" % email


@task(max_retries=10, default_retry_delay=10)
def confirmation_email(email, **kwargs):
    """

    Args:
        email:
        kwargs:
    """
    try:
        letter = Letter()
        letter.sender = 'support@yottos.com'
        letter.sender_name = 'Yottos GetMyAd'
        letter.recipients = email
        letter.subject = u'Подтверждение заявки на вывод средств в Yottos GetMyAd'
        letter.template = '/users/money_out/confirmation.mako.txt'
        letter.set_message(**kwargs)
        letter.send('mail.yottos.com', 25, 'support@yottos.com', '57fd8824')
    except Exception as ex:
        print "sendmail failed to %s: %s (retry #%s)" % (email, ex, kwargs.get('task_retries', 0))
        confirmation_email.retry(args=[email], kwargs=kwargs, exc=ex)
    else:
        print "sendmail to %s ok" % email


@task(max_retries=10, default_retry_delay=10, acks_late=True, ignore_result=True, queue='small-image')
def small_resize_image(res, campaign_id, work, **kwargs):
    """

    Args:
        res:
        campaign_id:
        work:
        kwargs:
    """
    resize_image(res, campaign_id, work, **kwargs)


@task(max_retries=10, default_retry_delay=10, acks_late=True, ignore_result=True, queue='image')
def resize_image(res, campaign_id, work, **kwargs):
    """

    Args:
        res:
        campaign_id:
        work:
        kwargs:
    """
    print "------------------------------------------------"
    try:
        db = _mongo_main_db()

        def resize_and_upload_image(db, urls, trum_height, trum_width, logo):
            ''' Пережимает изображение по адресу ``url`` до размеров
                ``height``x``width`` и заливает его на ftp для раздачи статики.
                Возвращает url нового файла или пустую строку в случае ошибки.
            '''
            try:
                def chdir(ftp, dir):
                    """

                    Args:
                        ftp:
                        dir:
                    """
                    if directory_exists(ftp, dir) is False:  # (or negate, whatever you prefer for readability)
                        ftp.mkd(dir)
                    ftp.cwd(dir)

                def directory_exists(ftp, dir):
                    """

                    Args:
                        ftp:
                        dir:

                    Returns:

                    """
                    filelist = []
                    ftp.retrlines('LIST', filelist.append)
                    for f in filelist:
                        if f.split()[-1] == dir and f.upper().startswith('D'):
                            return True
                    return False

                def ftp_loader(png, webp):
                    """

                    Args:
                        png:
                        webp:

                    Returns:

                    """
                    new_filename = uuid1().get_hex()
                    for host in cdn_ftp_list:
                        png.seek(0)
                        webp.seek(0)
                        buf_png = png
                        buf_webp = webp
                        try:
                            ftp = ftplib.FTP(host=host, timeout=1200)
                            ftp.login(cdn_ftp_user, cdn_ftp_password)
                            chdir(ftp, cdn_ftp_path)
                            chdir(ftp, 'img0')
                            chdir(ftp, new_filename[:2])
                            ftp.storbinary('STOR %s' % new_filename + '.png', buf_png)
                            ftp.storbinary('STOR %s' % new_filename + '.webp', buf_webp)
                            ftp.close()
                        except Exception as ex:
                            print "ftp:%s %s" % (host, ex)
                    return new_filename

                def resizer(url, trum_height, trum_width, logo):
                    """

                    Args:
                        url:
                        trum_height:
                        trum_width:
                        logo:

                    Returns:

                    """
                    opener = urllib2.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    response = opener.open(url)
                    f = cStringIO.StringIO(response.read())
                    i = Image.open(f).convert('RGBA')
                    width, height = i.size
                    if logo != '':
                        response = opener.open(logo)
                        f = cStringIO.StringIO(response.read())
                        l = Image.open(f).convert('RGBA')
                        l.thumbnail((trum_height, trum_width), Image.ANTIALIAS)
                    else:
                        l = None

                    if width > height:
                        first_box = (0, 0, width, 1)
                        second_box = (0, height - 1, width, height)
                        mod = (width - height) % 2
                        if mod == 0:
                            attach_counter_r = (width - height) / 2
                            attach_counter_l = (width - height) / 2
                        else:
                            attach_counter_r = (width - height) / 2
                            attach_counter_l = ((width - height) / 2) + 1
                        size = (width, width)
                        if l is None:
                            ratio = 'v'
                        else:
                            ratio = 'vl'

                    elif width < height:
                        first_box = (0, 0, 1, height)
                        second_box = (width - 1, 0, width, height)
                        mod = (height - width) % 2
                        if mod == 0:
                            attach_counter_r = (height - width) / 2
                            attach_counter_l = (height - width) / 2
                        else:
                            attach_counter_r = (height - width) / 2
                            attach_counter_l = ((height - width) / 2) + 1
                        size = (height, height)
                        ratio = 'h'
                    else:
                        size = (width, height)
                        attach_counter = 0
                        ratio = 'c'

                    image = Image.new("RGBA", size, (0, 0, 0))

                    if ratio != 'c':
                        first_line = i.crop(first_box)
                        cw, ch = first_line.size
                        percent = ((cw * ch) / 100.0)
                        color_count_first_line = first_line.getcolors(1024)
                        color_count_first_line.sort(key=lambda x: x[0], reverse=True)
                        first_line = Image.new("RGBA", (cw, ch), color_count_first_line[0][1])

                        second_line = i.crop(second_box)
                        cw, ch = second_line.size
                        percent = ((cw * ch) / 100.0)
                        color_count_second_line = second_line.getcolors(1024)
                        color_count_second_line.sort(key=lambda x: x[0], reverse=True)
                        second_line = Image.new("RGBA", (cw, ch), color_count_second_line[0][1])

                    if ratio == 'v':
                        image.paste(i, (0, attach_counter_r + 1))
                        counter = attach_counter_r
                        while counter > 0:
                            image.paste(first_line, (0, counter))
                            counter -= 1
                        counter = attach_counter_l
                        while counter > 0:
                            image.paste(second_line, (0, size[1] - counter))
                            counter -= 1
                    elif ratio == 'vl':
                        image.paste(i, (0, 0))
                        counter = attach_counter_r + attach_counter_l
                        while counter > 0:
                            image.paste(second_line, (0, size[1] - counter))
                            counter -= 1
                    elif ratio == 'h':
                        image.paste(i, (attach_counter_r + 1, 0))
                        counter = attach_counter_r
                        while counter > 0:
                            image.paste(first_line, (counter, 0))
                            counter -= 1
                        counter = attach_counter_l
                        while counter > 0:
                            image.paste(second_line, (size[1] - counter, 0))
                            counter -= 1
                    else:
                        image.paste(i, (0, 0))
                    if l is None:
                        image.thumbnail((trum_height, trum_width), Image.ANTIALIAS)
                    else:
                        image.thumbnail((trum_height, trum_width), Image.ANTIALIAS)
                        image.paste(l, (image.size[0] - l.size[0], image.size[1] - l.size[1]), l)
                    image = image.convert('RGB')
                    return [image, width, height]

                if not cdn_server_url or not cdn_ftp:
                    print 'Не заданы настройки сервера CDN. Проверьте .ini файл.'
                    return ''
                size_key = '%sx%s' % (trum_height, trum_width)

                result = []
                urlList = urls.split(',')
                for url in urlList:
                    rec = db.image.find_one({'src': url.strip(), size_key: {'$exists': True}, 'logo': logo})
                    if rec:
                        old_url = rec[size_key].get('url', '')
                        if old_url != '':
                            result.append(old_url)
                            continue

                    image = resizer(url, trum_height, trum_width, logo)

                    buf_png = cStringIO.StringIO()
                    buf_webp = cStringIO.StringIO()

                    image[0].save(buf_png, 'PNG')  # , optimize=True)
                    image[0].save(buf_webp, 'WebP')  # , lossless=True)

                    buf_png.seek(0)
                    buf_webp.seek(0)

                    new_filename = ftp_loader(buf_png, buf_webp)
                    new_url = cdn_server_url + 'img0/' + new_filename[:2] + '/' + new_filename + '.png'
                    db.image.update({'src': url, 'logo': logo},
                                    {'$set': {size_key: {'url': new_url,
                                                         'w': trum_width,
                                                         'h': trum_height,
                                                         'realWidth': image[1],
                                                         'realHeight': image[2],
                                                         'dt': datetime.datetime.now()
                                                         }}},
                                    upsert=True, w=1)
                    result.append(new_url)
                return " , ".join(result)
            except Exception as ex:
                print ex
                print url
                print "image failed"
                print "------------------------------------------------"
                return ''

        for key, value in res.items():
            url, trum_height, trum_width, logo = value
            image = resize_and_upload_image(db, url, trum_height, trum_width, logo)
            db.offer.update({'guid': key, },
                            {'$set': {"image": image}},
                            upsert=False, w=1)
        if campaign_id is not None and work:
            campaign_update(campaign_id)
    except Exception as ex:
        print "image failed to %s: %s (retry #%s)" % (campaign_id, ex, kwargs.get('task_retries', 0))
        resize_image.retry(args=[res, campaign_id, work], kwargs=kwargs, exc=ex)
    else:
        print "image to %s ok" % campaign_id
        print "------------------------------------------------"


@task(max_retries=10, ignore_result=True, acks_late=True, default_retry_delay=10)
def campaign_offer_update(campaign_id, **kwargs):
    ''' Обновляет рекламную кампанию ``campaign_id``.
    
    При обновлении происходит получение от AdLoad нового списка предложений и
    общей информации о кампании.
    
    Если кампания не была запущена, ничего не произойдёт.
    
    Если в кампании нет активных предложений, она будет остановлена.
    '''
    try:
        from getmyad.model.Campaign import Campaign
        from getmyad.model.Offer import Offer
        from getmyad.lib.adload_data import AdloadData

        print "Create connection"
        db = _mongo_main_db()
        connection_adload = mssql_connection_adload()

        def check_image(urls, height, width, logo):
            ''' Пережимает изображение по адресу ``url`` до размеров
                ``height``x``width`` и заливает его на ftp для раздачи статики.
                Возвращает url нового файла или пустую строку в случае ошибки.
            '''
            try:
                print "-------------------------------"
                print "Check image"
                size_key = '%sx%s' % (height, width)
                result = []
                urlList = urls.split(',')
                for url in urlList:
                    rec = db.image.find_one({'src': url.strip(), size_key: {'$exists': True}, 'logo': logo})
                    if rec:
                        print "Image Exist"
                        href = rec[size_key].get('url')
                        print href
                        result.append(href)
                        print "-------------------------------"
                if len(result) == len(urlList):
                    return " , ".join(result)
                return False
            except Exception as ex:
                print ex
                print "-------------------------------"
                return False

        a = datetime.datetime.now()
        campaign_id = campaign_id.lower()
        camp = Campaign(campaign_id, db)

        try:
            camp.load()
        except Campaign.NotFoundError:
            print 'Campaign is not running'
            return
        campaign_stop(campaign_id)
        camp.last_update = datetime.datetime.now()
        camp.project = 'adload'
        camp.update_status = 'start'
        work = camp.is_working()
        camp.save()
        ad = AdloadData(connection_adload=connection_adload)
        offers = ad.offers_list(campaign_id, camp.load_count)
        offers_len = len(offers)
        if offers_len < 1:
            print "Offers not found"
            camp.update_status = 'complite'
            camp.last_update = datetime.datetime.now()
            camp.save()
            return
        small = False
        if offers_len < 100:
            small = True
        elif offers_len > 50000:
            db.offer.remove({'campaignId': campaign_id}, w=3, j=True)
        print "Offers len", offers_len
        db.offer.remove({'campaignId': campaign_id, 'hash': {'$exists': False}}, w=1)

        ctr = 0.06
        uniqueHits_campaign = camp.UnicImpressionLot
        campaign_id_int = camp.id_int
        contextOnly_campaign = camp.contextOnly
        retargeting_campaign = camp.retargeting
        campaignTitle = camp.title
        res_task_img = {}

        pipeline = [
            {'$match': {'hash': {'$exists': True}, 'campaignId': campaign_id}},
            {'$group': {'_id': '$hash'}}
        ]
        hashes = []
        cursor = db.offer.aggregate(pipeline=pipeline, cursor={})
        for doc in cursor:
            hashes.append(doc['_id'])

        print "Start offer processed"
        for x in offers:
            if offers_len < 10000:
                image = check_image(x['image'], 210, 210, x['logo'])
            else:
                image = False
            if not image:
                res_task_img[x['id']] = [x['image'], 210, 210, x['logo']]
                image = ""
            offer_cost = float(x.get('ClickCost', '0.0'))
            offer = Offer(x['id'], db)
            offer.accountId = x['accountId'].lower()
            offer.title = x['title']
            offer.price = x['price']
            offer.url = x['url']
            offer.campaignTitle = campaignTitle
            offer.image = image
            offer.description = x['description']
            offer.date_added = x['dateAdded']
            offer.campaign = campaign_id
            offer.campaign_int = campaign_id_int
            offer.listAds = ['ALL']
            offer.isOnClick = True
            offer.type = 'teaser'
            offer.uniqueHits = uniqueHits_campaign
            offer.retargeting = retargeting_campaign
            retarg = x.get('RetargetingID', '')
            offer.RetargetingID = retarg.strip()
            offer.Recommended = x.get('Recommended', '')
            offer.width = -1
            offer.height = -1
            offer.rating = round(((ctr * offer_cost) * 100000), 4)
            offer.full_rating = round(((ctr * offer_cost) * 100000), 4)
            offer.cost = offer_cost
            offer.hash = offer.createOfferHash()
            if offer.hash not in hashes:
                offer.save()
            else:
                offer.update()
                hashes.remove(offer.hash)
            if len(res_task_img) >= 10:
                if small:
                    small_resize_image.delay(res_task_img, None, work)
                else:
                    resize_image.delay(res_task_img, None, work)
                res_task_img = {}

        if small:
            small_resize_image.delay(res_task_img, campaign_id, work)
        else:
            resize_image.delay(res_task_img, campaign_id, work)
        print "Start remove offers"
        db.offer.remove({'campaignId': campaign_id, 'hash': {'$in': hashes}}, w=1)
        b = datetime.datetime.now()
        c = b - a
        print "Load", c.seconds
    except Exception as ex:
        print "offer load failed to %s: %s (retry #%s)" % (campaign_id, ex, kwargs.get('task_retries', 0))
        campaign_offer_update.retry(args=[campaign_id], kwargs=kwargs, exc=ex)
    else:
        camp.load()
        camp.update_status = 'complite'
        camp.last_update = datetime.datetime.now()
        camp.save()
        if work:
            campaign_update(campaign_id)
        print "Finish load", campaign_id


@task(max_retries=10, default_retry_delay=10)
def delete_account(login, **kwargs):
    """

    Args:
        login:
        kwargs:
    """
    try:
        print "Delete Account"
        db = _mongo_main_db()
        informer_list = [x['guid'] for x in db.informer.find({'user': login})]
        domain_list = []
        for x in db.domain.find({'login': login}):
            y = x.get('domains', {})
            for key, value in y.iteritems():
                domain_list.append(value)
        for x in db.user.domains.find({'login': login}):
            y = x.get('domains', [])
            for value in y:
                domain_list.append(value)
        print db.stats_user_summary.remove({'user': login})
        print db.users.remove({'login': login})
        print db.informer.remove({'user': login})
        print db.domain.remove({'login': login})
        print db.user.domains.remove({'login': login})
        print db.domain.categories.remove({'domain': {'$in': domain_list}})
        print db.money_out_request.remove({'user.login': login})
        print db.stats_daily.rating.remove({'adv': {'$in': informer_list}})
        print db.stats_daily_adv.remove({'user': login})
        print db.stats_daily_domain.remove({'user': login})
        print db.stats_daily_user.remove({'user': login})
        account_update(login)
    except Exception as ex:
        print "account delete failed to %s: %s (retry #%s)" % (login, ex, kwargs.get('task_retries', 0))
        delete_account.retry(args=[login], kwargs=kwargs, exc=ex)
