# -*- coding: utf-8 -*-
import linecache
import sys
import traceback
from uuid import uuid1
import cStringIO
from eventlet.green import urllib2
import datetime
import pymssql
import time

import itertools
import mimetools
import mimetypes

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

# Параметры FTP для заливки статических файлов на сервер CDN
cdn_server_url = 'https://cdn.yottos.com/'
cdn_api_list = ['cdn.api.srv-10.yottos.com', 'cdn.api.srv-11.yottos.com', 'cdn.api.srv-12.yottos.com']


class MultiPartForm(object):
    __slots__ = ['files', 'boundary']

    def __init__(self):
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return

    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return

    def __str__(self):
        parts = []
        part_boundary = '--' + self.boundary

        parts.extend(
            [part_boundary,
             'Content-Disposition: file; name="%s"; filename="%s"' % \
             (field_name, filename),
             'Content-Type: %s' % content_type,
             '',
             body,
             ]
            for field_name, filename, content_type, body in self.files
        )

        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)


def send(url, filename, file, iteration=None):
    try:
        form = MultiPartForm()
        form.add_file('file', filename, file)
        body = str(form)
        request = urllib2.Request(url)
        request.add_header('X-Authentication', 'f9bf78b9a18ce6d46a0cd2b0b86df9da')
        request.add_header('User-agent', 'Mozilla/5.0')
        request.add_header('Content-type', form.get_content_type())
        request.add_header('Content-length', len(body))
        request.add_data(body)
        urllib2.urlopen(request)
    except Exception as e:
        print(e)
        if iteration is None:
            iteration = 0
        if iteration <= 5:
            iteration += 1
            send(url, filename, file, iteration)
        else:
            raise Exception(e)


def _mongo_connection():
    ''' Возвращает Connection к серверу MongoDB '''
    try:
        connection = pymongo.MongoClient(host=MONGO_HOST)
    except pymongo.errors.AutoReconnect:
        # Пауза и повторная попытка подключиться
        time.sleep(1)
        connection = pymongo.MongoClient(host=MONGO_HOST)
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


@task(max_retries=10, default_retry_delay=10, acks_late=False, ignore_result=True, queue='small-image')
def small_resize_image(res, campaign_id, work, **kwargs):
    """

    Args:
        res:
        campaign_id:
        work:
        kwargs:
    """
    resize_image(res, campaign_id, work, **kwargs)


@task(max_retries=10, default_retry_delay=10, acks_late=False, ignore_result=True, queue='image')
def resize_image(res, campaign_id, work, **kwargs):
    """

    Args:
        res:
        campaign_id:
        work:
        kwargs:
    """
    try:
        db = _mongo_main_db()

        def resize_and_upload_image(db, urls, trum_height, trum_width, logo):
            ''' Пережимает изображение по адресу ``url`` до размеров
                ``height``x``width`` и заливает его на ftp для раздачи статики.
                Возвращает url нового файла или пустую строку в случае ошибки.
            '''
            try:

                def cdn_loader(png, webp):
                    new_filename = uuid1().get_hex()
                    for host in cdn_api_list:
                        png.seek(0)
                        webp.seek(0)
                        send_png_url = 'http://%s/img1/%s/%s.png' % (host, new_filename[:2], new_filename)
                        send_webp_url = 'http://%s/img1/%s/%s.webp' % (host, new_filename[:2], new_filename)
                        send(send_png_url, '%s.png' % new_filename, png)
                        send(send_webp_url, '%s.webp' % new_filename, webp)
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
                    try:
                        response = opener.open(url)
                    except urllib2.HTTPError, e:
                        raise Exception('HTTPError = ' + str(e.code))
                    except urllib2.URLError, e:
                        raise Exception('URLError = ' + str(e.reason))
                    f = cStringIO.StringIO(response.read())
                    i = Image.open(f).convert('RGBA')
                    width, height = i.size
                    if logo != '':
                        try:
                            response = opener.open(url)
                        except urllib2.HTTPError, e:
                            raise Exception('HTTPError = ' + str(e.code))
                        except urllib2.URLError, e:
                            raise Exception('URLError = ' + str(e.reason))
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
                        color_count_first_line = first_line.getcolors(max(width, height))
                        color_count_first_line.sort(key=lambda x: x[0], reverse=True)
                        first_line = Image.new("RGBA", (cw, ch), color_count_first_line[0][1])

                        second_line = i.crop(second_box)
                        cw, ch = second_line.size
                        percent = ((cw * ch) / 100.0)
                        color_count_second_line = second_line.getcolors(max(width, height))
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

                if not cdn_server_url or not cdn_api_list:
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

                    try:
                        image = resizer(url, trum_height, trum_width, logo)
                    except Exception as ex:
                        exc_type, exc_obj, tb = sys.exc_info()
                        f = tb.tb_frame
                        trace = ''.join(traceback.format_tb(tb))
                        lineno = tb.tb_lineno
                        filename = f.f_code.co_filename
                        linecache.checkcache(filename)
                        line = linecache.getline(filename, lineno, f.f_globals)
                        print('----------------------------------------------')
                        print("image failed", url, ex)
                        print(
                        'EXCEPTION IN ({}, LINE {} "{}"): {} {}'.format(filename, lineno, line.strip(), exc_obj, trace))
                        print('----------------------------------------------')
                    else:
                        buf_png = cStringIO.StringIO()
                        buf_webp = cStringIO.StringIO()

                        image[0].save(buf_png, 'PNG')  # , optimize=True)
                        image[0].save(buf_webp, 'WebP')  # , lossless=True)

                        buf_png.seek(0)
                        buf_webp.seek(0)

                        new_filename = cdn_loader(buf_png, buf_webp)
                        new_url = cdn_server_url + 'img1/' + new_filename[:2] + '/' + new_filename + '.png'
                        db.image.update({'src': url.strip(), 'logo': logo},
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
                exc_type, exc_obj, tb = sys.exc_info()
                f = tb.tb_frame
                trace = ''.join(traceback.format_tb(tb))
                lineno = tb.tb_lineno
                filename = f.f_code.co_filename
                linecache.checkcache(filename)
                line = linecache.getline(filename, lineno, f.f_globals)
                print('----------------------------------------------')
                print('EXCEPTION IN ({}, LINE {} "{}"): {} {}'.format(filename, lineno, line.strip(), exc_obj, trace))
                print('----------------------------------------------')
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
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        trace = ''.join(traceback.format_tb(tb))
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print('----------------------------------------------')
        print "image failed to %s: %s (retry #%s)" % (campaign_id, ex, kwargs.get('task_retries', 0))
        print('EXCEPTION IN ({}, LINE {} "{}"): {} {}'.format(filename, lineno, line.strip(), exc_obj, trace))
        print('----------------------------------------------')
        resize_image.retry(args=[res, campaign_id, work], kwargs=kwargs, exc=ex)


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
        campaign_id_int = camp.id_int
        retargeting_campaign = camp.retargeting
        campaignTitle = camp.title

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
            res_task_img = {}
            if offers_len < 10000:
                image = check_image(x.image, 210, 210, x.logo)
            else:
                image = False
            if not image:
                res_task_img[x.id] = [x.image, 210, 210, x.logo]
                image = ""
            offer = Offer(x.id, db)
            offer.accountId = x.accountId.lower()
            offer.title = x.title
            offer.price = x.price
            offer.url = x.url
            offer.image = image
            offer.description = x.description
            offer.date_added = x.dateAdded
            offer.RetargetingID = x.RetargetingID
            offer.Recommended = x.Recommended
            offer.cost = x.ClickCost
            offer.campaignTitle = campaignTitle
            offer.campaign = campaign_id
            offer.campaign_int = campaign_id_int
            offer.retargeting = retargeting_campaign
            offer.rating = round(((ctr * offer.cost) * 100000), 4)
            offer.full_rating = round(((ctr * offer.cost) * 100000), 4)
            if offer.createOfferHash not in hashes:
                offer.save()
            else:
                offer.update()
                hashes.remove(offer.hash)
            if small:
                small_resize_image.delay(res_task_img, None, work)
            else:
                resize_image.delay(res_task_img, None, work)

        if small:
            small_resize_image.delay({}, campaign_id, work)
        else:
            resize_image.delay({}, campaign_id, work)
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
        login:*

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
