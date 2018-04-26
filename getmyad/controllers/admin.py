# -*- coding: UTF-8 -*-
import logging
import erequests as requests

from getmyad.lib.base import BaseController
from getmyad.model import InformerFtpUploader, MoneyOutRequest
from pylons import app_globals
from getmyad.lib import helpers as h

log = logging.getLogger(__name__)


class AdminController(BaseController):
    def update_reserve(self):
        ''' Перезаливка заглушек на FTP '''
        link = []
        headers = {'X-Cache-Update': '1'}
        cdns = ['http://cdn.srv-10.yottos.com', 'http://cdn.srv-11.yottos.com', 'http://cdn.srv-12.yottos.com']
        for i in app_globals.db.informer.find({}, ['guid']):
            guid = i['guid']
            InformerFtpUploader(guid).upload()
            link.append('/block/%s.json' % guid)
            link.append('/block/%s.js' % guid)
        for item in link:
            for cdn in cdns:
                url = '%s%s' % (cdn, item)
                r = requests.get(url, headers=headers, verify=False)
                print('%s - %s' % (url, r.status_code))

    def PendingMoneyOutRequests(self):
        ''' Список заявок на вывод средств, ожидающих подтверждения '''
        links = []
        for x in app_globals.db.money_out_request.find({'user_confirmed': {'$ne': True},
                                                        'confirm_guid': {'$exists': True}}):
            url = h.url_for(controller='admin',
                            action='ResendConfirmation',
                            id=x.get('confirm_guid'))
            links.append((url, x['date'], x['user']['login']))
        return u"<h2>Неподтверждённые заявки: %s</h2>" % \
               h.ul(map(lambda x: h.link_to('%s %s' % (x[1], x[2]), x[0]), links))

    def ResendConfirmation(self, id):
        ''' Повторно отправляет заявки на вывод средств '''
        m = MoneyOutRequest()
        m.load(id)
        m.send_confirmation_email()
