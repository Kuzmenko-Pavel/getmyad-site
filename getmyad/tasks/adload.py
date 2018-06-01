# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

import cStringIO
from io import BytesIO
import datetime
import pymssql
import sys
import time
from uuid import uuid4

import magic
import pymongo
from pymongo import WriteConcern
from pymongo.errors import BulkWriteError
import erequests as requests
from PIL import Image
from amqplib import client_0_8 as amqp
from celery.task import task

from getmyad.lib.adload_data import AdloadData
from getmyad.model.Campaign import Campaign
from getmyad.tasks.offer import Offer

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

GETMYAD_XMLRPC_HOST = 'https://getmyad.yottos.com/rpc'
MONGO_HOST = 'srv-5.yottos.com:27018,srv-5.yottos.com:27020,srv-5.yottos.com:27019'
MONGO_DATABASE = 'getmyad_db'

image_trumb_height_width = (210, 210)

# Параметры FTP для заливки статических файлов на сервер CDN
cdn_server_url = 'https://cdn.yottos.com'
cdn_api_list = ['http://cdn.api.srv-10.yottos.com', 'http://cdn.api.srv-11.yottos.com', 'http://cdn.api.srv-12.yottos.com']


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
    conn = amqp.Connection(host='amqp.yottos.com',
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
    print("AMQP campaign_update %s" % campaign_id)


def campaign_stop(campaign_id):
    ''' Отправляет уведомление об обновлении рекламной кампании ``campaign_id`` '''
    ch_worker = _get_worker_channel()
    msg = amqp.Message(campaign_id)
    ch_worker.basic_publish(msg, exchange='getmyad', routing_key='campaign.stop')
    ch_worker.close()
    print("AMQP campaign_stop %s" % campaign_id)


def account_update(login):
    ''' Отправляет уведомление об изменении в аккаунте ``login`` '''
    ch_worker = _get_worker_channel()
    msg = amqp.Message(login)
    ch_worker.basic_publish(msg, exchange='getmyad', routing_key='account.update')
    ch_worker.close()
    try:
        print("AMQP Account update %s" % login)
    except Exception as e:
        print(e)


def mssql_connection_adload():
    """

    Returns:

    """
    pymssql.set_max_connections(450)
    conn = pymssql.connect(host='srv-3.yottos.com',
                           user='web',
                           password='odif8duuisdofj',
                           database='AdLoad',
                           as_dict=True,
                           charset='cp1251')
    conn.autocommit(True)
    return conn


def check_image(db, url, logo):
    try:
        rec = db.images.find_one({'src': url.strip(), 'logo': logo})
        if rec:
            return rec.get('url')
        return None
    except Exception as ex:
        print(ex)
        return None


def send(url, filename, obj, iteration=None):
    try:
        headers = {
            'X-Authentication': 'f9bf78b9a18ce6d46a0cd2b0b86df9da',
            'User-agent': 'Mozilla/5.0'
        }
        mime = magic.Magic(mime=True)
        obj.seek(0)
        content_type = mime.from_buffer(obj.read())
        obj.seek(0)
        files = {'file': (filename, obj.read(), content_type)}
        r = requests.post(url, headers=headers, files=files)
        if r.status_code != requests.codes.ok:
            raise Exception('URLError = %s ' % r.status_code)
    except Exception as e:
        print('send error %s %s' % url, e)
        if iteration is None:
            iteration = 0
        if iteration <= 1:
            iteration += 1
            send(url, filename, obj, iteration)
        else:
            raise Exception(e)


def cdn_loader(png, webp):
    if not cdn_server_url or not cdn_api_list:
        raise Exception('Wrong settings')
    new_filename = uuid4().get_hex()
    url_path = datetime.datetime.now().strftime('img10/%m/%d')
    for host in cdn_api_list:
        png.seek(0)
        url = '%s/%s/%s.png' % (host, url_path, new_filename)
        send(url, '%s.png' % new_filename, png)

        webp.seek(0)
        url = '%s/%s/%s.webp' % (host, url_path, new_filename)
        send(url, '%s.webp' % new_filename, webp)
    return '%s/%s/%s.png' % (cdn_server_url, url_path, new_filename)


def resizer(url, trum_height, trum_width, logo):
    """

    Args:
        url:
        trum_height:
        trum_width:
        logo:

    Returns:

    """
    l = None
    headers = {
        'User-agent': 'Mozilla/5.0'
    }
    r = requests.get(url, headers=headers)
    if r.status_code != requests.codes.ok:
        raise Exception('URLError = %s %s' % (r.status_code, url))
    i = Image.open(BytesIO(r.content)).convert('RGBA')
    width, height = i.size
    if logo and logo != '':
        r = requests.get(logo, headers=headers)
        if r.status_code != requests.codes.ok:
            raise Exception('URLError = %s %s' % (r.status_code, logo))
        l = Image.open(BytesIO(r.content)).convert('RGBA')
        l.thumbnail((trum_height, trum_width), Image.ANTIALIAS)

    first_box = (None, None, None, None)
    second_box = (None, None, None, None)
    attach_counter_r = None
    attach_counter_l = None
    first_line = None
    second_line = None
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
        ratio = 'c'

    image = Image.new("RGBA", size, (0, 0, 0))

    if ratio != 'c':
        first_line = i.crop(first_box)
        cw, ch = first_line.size
        color_count_first_line = first_line.getcolors(max(width, height))
        color_count_first_line.sort(key=lambda x: x[0], reverse=True)
        first_line = Image.new("RGBA", (cw, ch), color_count_first_line[0][1])

        second_line = i.crop(second_box)
        cw, ch = second_line.size
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

    return [image.convert('RGB'), width, height]


def resize_and_upload_image(db, urls, logo):
    ''' Пережимает изображение по адресу ``url`` до размеров
        ``height``x``width`` и заливает его на ftp для раздачи статики.
        Возвращает url нового файла или пустую строку в случае ошибки.
    '''
    try:
        trum_height, trum_width = image_trumb_height_width
        result = []
        coll = db.get_collection('images', write_concern=WriteConcern(w=0))
        for url in urls:
            rec = check_image(db, url, logo)
            if rec:
                result.append(rec)
                continue

            try:
                image = resizer(url, trum_height, trum_width, logo)
            except Exception as ex:
                raise Exception('Image resizer filed %s' % ex)

            buf_png = cStringIO.StringIO()
            buf_webp = cStringIO.StringIO()

            image[0].save(buf_png, 'PNG')  # , optimize=True)
            image[0].save(buf_webp, 'WebP')  # , lossless=True)

            buf_png.seek(0)
            buf_webp.seek(0)

            cdn_url = cdn_loader(buf_png, buf_webp)
            coll.update({'src': url.strip(), 'logo': logo},
                        {'$set': {'url': cdn_url, 'dt': datetime.datetime.now()}}, upsert=True)
            result.append(cdn_url)
        return result
    except Exception as ex:
        print('resize_and_upload_image %s' % ex)
        return []


@task(max_retries=10, default_retry_delay=10, acks_late=False, ignore_result=True, queue='small-image')
def small_resize_image(offer_id=None, urls=None, logo=None, campaign_id=None, **kwargs):
    """

    Args:
        offer_id:
        urls:
        logo:
        campaign_id:
        kwargs:
    """
    resize_image(offer_id, urls, logo, campaign_id, **kwargs)


@task(max_retries=10, default_retry_delay=10, acks_late=False, ignore_result=True, queue='image')
def resize_image(offer_id=None, urls=None, logo=None, campaign_id=None, **kwargs):
    """

    Args:
        offer_id:
        urls:
        logo:
        campaign_id:
        kwargs:
    """
    try:
        db = _mongo_main_db()
        if offer_id and urls:
            images = resize_and_upload_image(db, urls, logo)
            coll = db.get_collection('offer', write_concern=WriteConcern(w=0))
            data = {"image":  " , ".join(images)}
            if len(urls) != len(images):
                data['image_hash'] = ''
            coll.update_many({'guid': offer_id, }, {'$set': data}, upsert=False)
        if campaign_id:
            campaign_update(campaign_id)
    except Exception as ex:
        print('Task resize_image %s' % ex)
        resize_image.retry(args=[offer_id, urls, logo, campaign_id], kwargs=kwargs, exc=ex)


@task(max_retries=10, default_retry_delay=10, acks_late=False, ignore_result=True, queue='preload-image')
def preload_image(urls=None, logo=None, **kwargs):
    """

    Args:
        offer_id:
        urls:
        logo:
        campaign_id:
        kwargs:
    """
    try:
        db = _mongo_main_db()
        if urls:
            resize_and_upload_image(db, urls, logo)
    except Exception as ex:
        print('Task preload_image %s' % ex)
        resize_image.retry(args=[urls, logo], kwargs=kwargs, exc=ex)


@task(max_retries=10, ignore_result=True, acks_late=True, default_retry_delay=10)
def campaign_offer_update(campaign_id, **kwargs):
    ''' Обновляет рекламную кампанию ``campaign_id``.
    
    При обновлении происходит получение от AdLoad нового списка предложений и
    общей информации о кампании.
    
    Если кампания не была запущена, ничего не произойдёт.
    
    Если в кампании нет активных предложений, она будет остановлена.
    '''
    start_time_main = time.time()
    try:
        db = _mongo_main_db()
        connection_adload = mssql_connection_adload()
        campaign_id = campaign_id.lower()
        camp = Campaign(campaign_id, db)

        try:
            camp.load()
        except Campaign.NotFoundError:
            return

        campaign_stop(campaign_id)
        camp.last_update = datetime.datetime.now()
        camp.project = 'adload'
        camp.update_status = 'start'
        work = camp.is_working()
        camp.save()
        with AdloadData(connection_adload=connection_adload) as ad:
            ad.offers_list(campaign_id, camp.load_count)
            start_time = time.time()
            offers_len = len(ad.offers)
            print("--- Count offers %s seconds ---" % (time.time() - start_time))
            if offers_len < 1:
                camp.update_status = 'complite'
                camp.last_update = datetime.datetime.now()
                camp.save()
                return
            task_resize_image = resize_image
            if offers_len < 100:
                task_resize_image = small_resize_image

            campaign_id_int = camp.id_int
            retargeting_campaign = camp.retargeting
            campaignTitle = camp.title

            pipeline = [
                {'$match': {'campaignId': campaign_id}},
                {'$group': {'_id': {'_id': '$_id', 'hash': '$hash', 'image_hash': '$image_hash'}}}
            ]
            start_time = time.time()
            cursor = db.offer.aggregate(pipeline=pipeline, cursor={}, allowDiskUse=True)
            hashes = {}
            image_hashes = {}
            for doc in cursor:
                hashes[doc['_id'].get('hash', '?')] = doc['_id']['_id']
                image_hashes[doc['_id'].get('image_hash', '?')] = doc['_id']['_id']

            print("--- Get Hashes %s seconds ---" % (time.time() - start_time))

            operations = []
            res_task_img = []
            coll = db.get_collection('offer', write_concern=WriteConcern(w=0))
            start_time_iter = time.time()
            for x in ad.offers.itervalues():
                offer = Offer(x['id'])
                offer.title = x['title']
                offer.price = x['price']
                offer.url = x['url']
                offer.description = x['description']
                offer.RetargetingID = x['RetargetingID']
                offer.Recommended = x['Recommended']
                offer.campaign = campaign_id
                offer.campaign_int = campaign_id_int
                offer.retargeting = retargeting_campaign

                offer.image = x['image'].split(',')
                offer.logo = x['logo']

                if offer.image_hash in image_hashes:
                    try:
                        del image_hashes[offer.image_hash]
                    except Exception as e:
                        print('remove hash %s' % str(e))
                else:
                    try:
                        preload_image.delay(offer.image, offer.logo)
                        res_task_img.append((offer.id, offer.image, offer.logo))
                    except Exception as ex:
                        print(ex, "offer.save", x['id'])

                if offer.hash in hashes:
                    try:
                        del hashes[offer.hash]
                    except Exception as e:
                        print('remove hash %s' % str(e))
                else:
                    try:
                        offer.cost = x['ClickCost']
                        offer.campaignTitle = campaignTitle
                        offer.accountId = x['accountId']
                        operations.append(offer.save)
                    except Exception as ex:
                        print(ex, "offer.save", x['id'])

                if len(res_task_img) >= 10000:
                    if operations:
                        start_time_bulk_write = time.time()
                        try:
                            coll.bulk_write(operations, ordered=False)
                        except BulkWriteError as bwe:
                            print(bwe.details)
                        print("--- Bulk Write %s seconds ---" % (time.time() - start_time_bulk_write))

                    start_time_task_img = time.time()
                    for task_img in res_task_img:
                        task_resize_image.delay(task_img[0], task_img[1], task_img[2])
                    print("--- Create image task %s seconds ---" % (time.time() - start_time_task_img))

                    res_task_img = []
                    operations = []

            print("--- Iterate offer %s seconds ---" % (time.time() - start_time_iter))
            for value in hashes.itervalues():
                operations.append(
                    pymongo.DeleteOne({'_id': value})
                )
            try:
                if operations:
                    start_time_bulk_write = time.time()
                    db.offer.bulk_write(operations, ordered=False)
                    print("--- Bulk Write End %s seconds %s ---" % (time.time() - start_time_bulk_write, len(operations)))
            except BulkWriteError as bwe:
                print(bwe.details)

            start_time_task_img = time.time()
            for task_img in res_task_img:
                task_resize_image.delay(task_img[0], task_img[1], task_img[2])
            if work:
                task_resize_image.delay(campaign_id=campaign_id)
            print("--- Create image task End %s seconds %s ---" % (time.time() - start_time_task_img, len(res_task_img)))

    except Exception as ex:
        campaign_offer_update.retry(args=[campaign_id], kwargs=kwargs, exc=ex)
    else:
        camp.load()
        camp.update_status = 'complite'
        camp.last_update = datetime.datetime.now()
        camp.save()
    print("--- Task execution %s seconds ---" % (time.time() - start_time_main))


@task(max_retries=10, default_retry_delay=10)
def delete_account(login, **kwargs):
    """

    Args:
        login:*

        kwargs:
    """
    try:
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
        print(db.stats_user_summary.remove({'user': login}))
        print(db.users.remove({'login': login}))
        print(db.informer.remove({'user': login}))
        print(db.domain.remove({'login': login}))
        print(db.user.domains.remove({'login': login}))
        print(db.domain.categories.remove({'domain': {'$in': domain_list}}))
        print(db.money_out_request.remove({'user.login': login}))
        print(db.stats_daily.rating.remove({'adv': {'$in': informer_list}}))
        print(db.stats_daily_adv.remove({'user': login}))
        print(db.stats_daily_domain.remove({'user': login}))
        print(db.stats_daily_user.remove({'user': login}))
        account_update(login)
    except Exception as ex:
        delete_account.retry(args=[login], kwargs=kwargs, exc=ex)
