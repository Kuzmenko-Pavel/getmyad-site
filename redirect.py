# encoding: utf-8
import base64
import datetime
import unittest
import urlparse
from getmyad.tasks import tasks
import sys
import pymongo

sys.stdout = sys.stderr

MONGO_HOST = '213.186.121.201:27018,213.186.121.84:27018,yottos.com'


def redirect(environ, start_response):
    def _redirect_to(url):
        ''' Перенаправление на ``url`` '''
        response_headers = [('Location', url),
                            ('Connection', 'close')]
        start_response("301 Moved Permanently", response_headers)
        return ""

    # Получаем словарь параметров
    try:
        # Отделяем дополнительные GET-параметры от основных,
        # закодированных в base64
        base64_encoded_params = environ['QUERY_STRING'].partition('&')[0]
        param_lines = base64.urlsafe_b64decode(base64_encoded_params) \
            .splitlines()
        params = dict([(x.partition('=')[0], x.partition('=')[2])
                       for x in param_lines])
        url = params.get('url')

        # Выделяем домен партнёра и добавляем его в целевой url
        if _need_yottos_partner_marker(offer_id=params.get('id')):
            partner_domain = urlparse.urlsplit(params.get('loc')).netloc
            if not partner_domain:
                partner_domain = _get_informer_domain(params.get('inf'))
            url = _add_url_param(url, 'yottos_partner',
                                 partner_domain or 'other')

        # Выделяем параметры для Attractora и добавляем их в целевой url
        if _need_yottos_attractor_marker(offer_id=params.get('id')):
            db = pymongo.Connection(MONGO_HOST).getmyad_db
            campaign_id = db.offer.find_one({'guid': params.get('id')}, ['campaignId'])['campaignId']
            url = _add_url_param(url, 'pk_campaign', str(campaign_id))
            url = _add_url_param(url, 'pk_kwd', str(params.get('id')))

    except Exception as e:
        print e
        return _redirect_to('http://yottos.com')

    try:
        tasks.process_click.delay(url=url,
                                  ip=environ['REMOTE_ADDR'],
                                  click_datetime=datetime.datetime.now(),
                                  offer_id=params.get('id'),
                                  informer_id=params.get('inf'),
                                  token=params.get('token'),
                                  server=params.get('server'))
    except Exception as ex:
        tasks.process_click(url=url,
                            ip=environ['REMOTE_ADDR'],
                            click_datetime=datetime.datetime.now(),
                            offer_id=params.get('id'),
                            informer_id=params.get('inf'),
                            token=params.get('token'),
                            server=params.get('server'))

    return _redirect_to(url or 'http://yottos.com')


def _add_url_param(url, param, value):
    ''' Добавляет параметр ``param`` со значением ``value`` в ``url`` '''
    splitted = list(urlparse.urlparse(url))
    if splitted[4]:
        splitted[4] += '&%s=%s' % (param, value)
    else:
        splitted[4] = '%s=%s' % (param, value)
    return urlparse.urlunparse(splitted)


def _get_informer_domain(informer_id):
    ''' Возвращает домен, к которому относится информер ``informer_id`` '''
    try:
        db = pymongo.Connection(MONGO_HOST).getmyad_db
        return str(db.informer.find_one({'guid': informer_id})['domain'])
    except (AttributeError, KeyError):
        return informer_id
    except pymongo.errors.AutoReconnect:
        return informer_id


def _need_yottos_partner_marker(offer_id):
    ''' Возвращает True, если к ссылке перехода на рекламное предложение
        ``offer_id`` необходимо добавить маркер yottos_partner=... '''
    try:
        db = pymongo.Connection(MONGO_HOST).getmyad_db
        campaign_id = db.offer.find_one({'guid': offer_id},
                                        ['campaignId'])['campaignId']
        need_marker = db.campaign.find_one({'guid': campaign_id},
                                           ['yottosPartnerMarker']) \
            .get('yottosPartnerMarker', True)
        return need_marker
    except (AttributeError, KeyError):
        return True
    except pymongo.errors.AutoReconnect:
        return True


def _need_yottos_attractor_marker(offer_id):
    ''' Возвращает True, если к ссылке перехода на рекламное предложение
        ``offer_id`` необходимо добавить маркер ... '''
    try:
        db = pymongo.Connection(MONGO_HOST).getmyad_db
        campaign_id = db.offer.find_one({'guid': offer_id},
                                        ['campaignId'])['campaignId']
        need_marker = db.campaign.find_one({'guid': campaign_id},
                                           ['yottosAttractorMarker']) \
            .get('yottosAttractorMarker', True)
        return need_marker
    except (AttributeError, KeyError):
        return True
    except pymongo.errors.AutoReconnect:
        return True


class TestAddParamToUrl(unittest.TestCase):
    def test_url_has_no_params(self):
        self.assertEqual(_add_url_param(
            'http://ex.com/index.php', 'key', 'value'),
            'http://ex.com/index.php?key=value')

    def test_url_has_one_param(self):
        self.assertEqual(_add_url_param(
            'http://ex.com/index.php?p=1', 'key', 'value'),
            'http://ex.com/index.php?p=1&key=value')

    def test_url_with_hash(self):
        self.assertEqual(_add_url_param(
            'http://ex.com/index.php?p=1#hash', 'key', 'value'),
            'http://ex.com/index.php?p=1&key=value#hash')

    def test_national_domain(self):
        self.assertEqual(_add_url_param(
            'http://тест.com/index.php?p=1#hash', 'key', 'value'),
            'http://тест.com/index.php?p=1&key=value#hash')


if __name__ == '__main__':
    unittest.main()

application = redirect
