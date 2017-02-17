# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from formencode import validators as v
from getmyad import model
from getmyad.controllers.advertise import AdvertiseController
from getmyad.controllers.main import MainController
from getmyad.lib import helpers as h
from getmyad.lib.base import BaseController, render
from getmyad.model import AccountReports, Account
from pylons import request, response, session, tmpl_context as c, url, \
    app_globals, config
from pylons.controllers.util import abort, redirect
from uuid import uuid1
import formencode
import json
import logging
import os
import pymongo
import time

log = logging.getLogger(__name__)


def current_user_check(f):
    ''' Декоратор. Проверка есть ли в сессии авторизованный пользователь'''
    def wrapper(*args):
        user = request.environ.get('CURRENT_USER')
        if not user:
            return h.userNotAuthorizedError()
        c.user = user
        return f(*args)
    return wrapper


def expandtoken(f):
    ''' Декоратор находит данные сессии по токену, переданному в параметре
        ``token`` и записывает их в ``c.info`` '''
    def wrapper(*args):
        try:
            token = request.params.get('token')
            c.info = session.get(token)
        except:
            # TODO: Ошибку на нормальной странице
            return h.userNotAuthorizedError()
        return f(*args)
    return wrapper


def authcheck(f):
    ''' Декоратор сравнивает текущего пользователя и пользователя,
        от которого пришёл запрос. '''
    def wrapper(*args):
        try:
            if c.info['user'] != session.get('user'):
                raise
        except NameError:
            raise TypeError(
                "Не задана переменная info во время вызова authcheck")
        except:
            # TODO: Ошибку на нормальной странице
            return h.userNotAuthorizedError()
        return f(*args)
    return wrapper


class PrivateController(BaseController):

    def __before__(self, action, **params):
        user = session.get('user')
        if user:
            request.environ['CURRENT_USER'] = user
            request.environ['IS_MANAGER'] = session.get('isManager', False)

    def index(self):
        """Основная страница статистики (кабинет пользователя) """
        user = request.environ.get('CURRENT_USER')
        if not user:
            return redirect(url(controller='main', action='signOut'))
        if request.environ['IS_MANAGER']:
            return redirect(url(controller='manager', action='index'))

        token = str(uuid1()).upper()
        session[token] = {'user': session.get('user')}
        session.save()
        c.token = token

        account = model.Account(user)
        try:
            account.load()
        except Account.NotFoundError:
            return MainController().signOut()

        ad = AdvertiseController()
        c.manager = account.getManagerInfo() 
        c.updateTime = model.updateTime()
        try:
            c.updateTimeUTC = int(time.mktime(c.updateTime.timetuple()) * 1000)
        except TypeError:
            c.updateTimeUTC = None
        c.accountSumm = account.report.balance()
        c.informers = account.informers()
        c.min_out_sum = account.min_out_sum
        c.money_out_paymentType = (account.money_out_paymentType or 
                                   ['webmoney_z'])
        c.moneyOutEnabled = (account.prepayment or
                             c.accountSumm >= c.min_out_sum)
        domains = account.domains.list()
        requests = account.domains.list_request()
        for x in requests:
            domains.append(str(x) + u' (ожидает подтверждения)')
        if (ad._domainsAdvertises('')):
            domains.append('')
        c.remove_domains = [(x, x) for x in domains]
        c.domains = h.jgridDataWrapper([(x, '') for x in domains])
        return render('/statistics.mako.html')

    @current_user_check
    def all_account_data(self):
        ''' Возвращает все данные, которые нужны для кабинета пользователя '''
        account = model.Account(c.user)
        try:
            account.load()
        except Account.NotFoundError:
            return MainController().signOut()

        ad = AdvertiseController()
        money_out_paymentType = account.money_out_paymentType or ['webmoney_z']
        return h.JSON({
            'accountSumm':      account.report.balance(),
            'accountOutSumm':      account.report.outBalance(),
            'chartData':        ad.days(json=False)
        })

    @current_user_check
    def accountIncome(self):
        """Возвращает данные о начислении денег на счёт"""
        ads = [x.guid for x in model.Account(c.user).informers()]
        db = app_globals.db
        data = db.stats.daily.adv.group(['date'],
                                        {'user': c.user},
                                        {
                                        'sum': 0,
                                        'unique': 0,
                                        'impressions_block': 0,
                                        },
                                        '''function(o,p) {
                                          p.sum += o.totalCost || 0;
                                          p.impressions_block += o.impressions_block || 0;
                                          p.unique += o.clicksUnique || 0;
                                        }''')
        data.sort(key=lambda x: x['date'])
        data.reverse()

        from math import ceil
        try:
            page = int(request.params.get('page'))
            rows = int(request.params.get('rows'))
        except:
            page = 1
            rows = 20

        totalPages = int(ceil(float(len(data)) / rows))
        data = data[(page - 1) * rows: page * rows]
        data = [{'id': index,
                 'cell': (
                    x['date'].strftime("%d.%m.%Y"),
                    x['impressions_block'],
                    x['unique'],
                    '%.2f грн' % ((x['sum'] / x['unique']) if x['unique'] else 0),
                    '%.2f грн' % x['sum']
                 )
                }
                    for index, x in enumerate(data)]
        return h.JSON({'total': totalPages,
                       'page': page,
                       'records': len(data),
                       'rows': data
                       })

    @current_user_check
    def moneyOutHistory(self):
        """История вывода денег"""
        table = self._moneyOutHistory_table_data(json=True)
        return table

    def _moneyOutHistory_table_data(self, json=True):
        """История вывода денег"""
        data = AccountReports(Account(c.user)).money_out_requests()
        data.sort(key=lambda x: x['date'], reverse=True)
        table = []
        for x in data:
            date = x['date'].strftime("%d.%m.%Y %H:%M")
            summ = h.formatMoney(x['summ'])
            protectionCode = x.get('protectionCode', '')
            protectionDate = x.get('protectionDate', '')
            protectionDate = protectionDate.strftime("%d.%m.%Y") if isinstance(protectionDate, datetime) else ''
            if not x.get('approved'):
                comment = u'заявка обрабатывается...'
            else:
                if x.get('comment'):
                    comment = u"подтверждена: %s" % x.get('comment')
                else:
                    comment = u"подтверждена"
            row = (date, x['paymentType'], summ, protectionCode, protectionDate, comment)
            table.append(row)
        return h.jgridDataWrapper(table, json=json)

    @current_user_check
    @expandtoken
    @authcheck
    def moneyOutSubmit(self):
        ''' Обрабатывает поданную заявку на вывод средств '''
        paymentType = request.params.get('moneyOut_paymentType')

        if paymentType == 'webmoney_z':
            return self._moneyOutSubmit_webmoney()

        elif paymentType == 'webmoney_r':
            return self._moneyOutSubmit_webmoney_r()

        elif paymentType == 'webmoney_u':
            return self._moneyOutSubmit_webmoney_u()

        elif paymentType == 'cash':
            return self._moneyOutSubmit_cash()
        
        elif paymentType == 'card':
            return self._moneyOutSubmit_card()

        elif paymentType == 'card_pb_ua':
            return self._moneyOutSubmit_card_pb_ua()
        
        elif paymentType == 'card_pb_us':
            return self._moneyOutSubmit_card_pb_us()

        elif paymentType == "factura":
            return self._moneyOutSubmit_factura()

        elif paymentType == "yandex":
            return self._moneyOutSubmit_yandex()

        else:
            errorMessage = u'<br/>\n Не выбран тип оплаты'
            return h.JSON({'error': True, 'msg': errorMessage, 'ok': False})

    def _moneyOutSubmit_webmoney(self):
        ''' Обработка заявки на вывод средств посредством webmoney '''
        schema = MoneyOutForm_web()
        try:
            form = schema.to_python(dict(request.params))
        except formencode.Invalid, error:
            errorMessage = '<br/>\n'.join(
                [x.msg for x in error.error_dict.values()])
            return h.JSON({'error': True, 'msg': errorMessage, 'ok': False})

        req = model.WebmoneyMoneyOutRequest()
        req.account = model.Account(c.user)
        req.ip = request.environ['REMOTE_ADDR']
        req.summ = form.get('moneyOut_summ')
        req.webmoney_login = form.get('moneyOut_webmoneyLogin')
        req.webmoney_account_number = form.get(
                                        'moneyOut_webmoneyAccountNumber')
        req.phone = form.get('moneyOut_phone')
        req.comment = form.get('moneyOut_comment', '')
        try:
            req.save()
            req.send_confirmation_email()
        except model.MoneyOutRequest.NotEnoughMoney:
            return h.JSON({'error': True,
                           'msg': u'Недостаточно средств для вывода!',
                           'ok': False})
        except model.MoneyOutRequest.NotConfirm:
            return h.JSON({'error': True,
                           'msg': u'Сушествуют необработанные заявки. Дождитесь ихней обработки.',
                           'ok': False})
        except Exception as ex:
            log.debug(unicode(ex))

        return h.JSON({'error': False,
                       'ok': True,
                       'msg': u'Заявка успешно принята'})

    def _moneyOutSubmit_webmoney_r(self):
        ''' Обработка заявки на вывод средств посредством webmoney '''
        schema = MoneyOutForm_web_r()
        try:
            form = schema.to_python(dict(request.params))
        except formencode.Invalid, error:
            errorMessage = '<br/>\n'.join(
                [x.msg for x in error.error_dict.values()])
            return h.JSON({'error': True, 'msg': errorMessage, 'ok': False})

        req = model.WebmoneyMoneyOutRequest_r()
        req.account = model.Account(c.user)
        req.ip = request.environ['REMOTE_ADDR']
        req.summ = form.get('moneyOut_summ_r')
        req.webmoney_login = form.get('moneyOut_webmoneyLogin_r')
        req.webmoney_account_number = form.get(
                                        'moneyOut_webmoneyAccountNumber_r')
        req.phone = form.get('moneyOut_phone_r')
        req.comment = form.get('moneyOut_comment_r', '')
        try:
            req.save()
            req.send_confirmation_email()
        except model.MoneyOutRequest.NotEnoughMoney:
            return h.JSON({'error': True,
                           'msg': u'Недостаточно средств для вывода!',
                           'ok': False})
        except model.MoneyOutRequest.NotConfirm:
            return h.JSON({'error': True,
                           'msg': u'Сушествуют необработанные заявки. Дождитесь ихней обработки.',
                           'ok': False})
        except Exception as ex:
            log.debug(unicode(ex))

        return h.JSON({'error': False,
                       'ok': True,
                       'msg': u'Заявка успешно принята'})

    def _moneyOutSubmit_webmoney_u(self):
        ''' Обработка заявки на вывод средств посредством webmoney '''
        schema = MoneyOutForm_web_u()
        try:
            form = schema.to_python(dict(request.params))
        except formencode.Invalid, error:
            errorMessage = '<br/>\n'.join(
                [x.msg for x in error.error_dict.values()])
            return h.JSON({'error': True, 'msg': errorMessage, 'ok': False})

        req = model.WebmoneyMoneyOutRequest_u()
        req.account = model.Account(c.user)
        req.ip = request.environ['REMOTE_ADDR']
        req.summ = form.get('moneyOut_summ_u')
        req.webmoney_login = form.get('moneyOut_webmoneyLogin_u')
        req.webmoney_account_number = form.get(
                                        'moneyOut_webmoneyAccountNumber_u')
        req.phone = form.get('moneyOut_phone_u')
        req.comment = form.get('moneyOut_comment_u', '')
        try:
            req.save()
            req.send_confirmation_email()
        except model.MoneyOutRequest.NotEnoughMoney:
            return h.JSON({'error': True,
                           'msg': u'Недостаточно средств для вывода!',
                           'ok': False})
        except model.MoneyOutRequest.NotConfirm:
            return h.JSON({'error': True,
                           'msg': u'Сушествуют необработанные заявки. Дождитесь ихней обработки.',
                           'ok': False})
        except Exception as ex:
            log.debug(unicode(ex))

        return h.JSON({'error': False,
                       'ok': True,
                       'msg': u'Заявка успешно принята'})

    def _moneyOutSubmit_yandex(self):
        ''' Обработка заявки на вывод средств посредством Яндекс Деньги '''
        schema = MoneyOutForm_yandex()
        try:
            form = schema.to_python(dict(request.params))            
        except formencode.Invalid, error:
            errorMessage = '<br/>\n'.join(
                [x.msg for x in error.error_dict.values()])
            return h.JSON({'error': True, 'msg': errorMessage, 'ok': False})

        req = model.YandexMoneyOutRequest()
        req.account = model.Account(c.user)
        req.ip = request.environ['REMOTE_ADDR']
        req.summ = form.get('moneyOut_yandexSumm')
        req.yandex_number = form.get('moneyOut_yandex_number')
        req.phone = form.get('moneyOut_yandex_phone')
        req.comment = form.get('moneyOut_yandex_comment', '')
        try:           
            req.save()
            req.send_confirmation_email()
        except model.MoneyOutRequest.NotEnoughMoney:
            return h.JSON({'error': True,
                           'msg': u'Недостаточно средств для вывода!',
                           'ok': False})
        except Exception as ex:
            log.debug(unicode(ex))

        return h.JSON({'error': False,
                       'ok': True,
                       'msg': u'Заявка успешно принята'})

    def _moneyOutSubmit_card(self):
        ''' Обработка заявки на вывод средств посредством пластиковой карты '''
        schema = MoneyOutForm_card()
        try:
            form = schema.to_python(dict(request.params))
        except formencode.Invalid, error:
            errorMessage = '<br/>\n'.join(
                            [x.msg for x in error.error_dict.values()])
            return h.JSON({'error': True, 'msg': errorMessage, 'ok': False})

        req = model.CardMoneyOutRequest()
        req.account = model.Account(c.user)
        req.ip = request.environ['REMOTE_ADDR']
        req.summ = form.get('moneyOut_cardSumm', '')
        req.comment = form.get('moneyOut_cardComment', '')
        req.card_number = form.get('moneyOut_cardNumber', '')
        req.card_name = form.get('moneyOut_cardName', '')
        req.card_type = form.get('moneyOut_cardType', '')
        req.card_currency = form.get('moneyOut_cardCurrency')
        req.expire_year = form.get('moneyOut_cardYear', '')
        req.expire_month = form.get('moneyOut_cardMonth', '')
        req.bank = form.get('moneyOut_cardBank', '')
        req.bank_mfo = form.get('moneyOut_cardBankMFO', '')
        req.bank_okpo = form.get('moneyOut_cardBankOKPO', '')
        req.bank_transit_account = form.get('moneyOut_cardBankTransitAccount',
                                            '')
        req.card_phone = form.get('moneyOut_cardPhone', '')
        try:
            req.save()
            req.send_confirmation_email()
        except model.MoneyOutRequest.NotEnoughMoney:
            return h.JSON({'error': True,
                           'msg': u'Недостаточно средств для вывода!',
                           'ok': False})
        except model.MoneyOutRequest.NotConfirm:
            return h.JSON({'error': True,
                           'msg': u'Сушествуют необработанные заявки. Дождитесь ихней обработки.',
                           'ok': False})
        except Exception as ex:
            log.debug(repr(ex))
        return h.JSON({'error': False,
           'ok': True,
           'msg': u'Заявка успешно принята'})

    def _moneyOutSubmit_card_pb_ua(self):
        ''' Обработка заявки на вывод средств посредством пластиковой карты '''
        schema = MoneyOutForm_card_pb_ua()
        try:
            form = schema.to_python(dict(request.params))
        except formencode.Invalid, error:
            errorMessage = '<br/>\n'.join(
                            [x.msg for x in error.error_dict.values()])
            return h.JSON({'error': True, 'msg': errorMessage, 'ok': False})

        req = model.CardMoneyOutRequest_pb_ua()
        req.account = model.Account(c.user)
        req.ip = request.environ['REMOTE_ADDR']
        req.summ = form.get('moneyOut_cardSumm_pb_ua', '')
        req.comment = form.get('moneyOut_cardComment_pb_ua', '')
        req.card_number = form.get('moneyOut_cardNumber_pb_ua', '')
        req.card_name = form.get('moneyOut_cardName_pb_ua', '')
        req.card_type = form.get('moneyOut_cardType_pb_ua', '')
        req.card_currency = form.get('moneyOut_cardCurrency_pb_ua')
        req.expire_year = form.get('moneyOut_cardYear_pb_ua', '')
        req.expire_month = form.get('moneyOut_cardMonth_pb_ua', '')
        req.card_phone = form.get('moneyOut_cardPhone_pb_ua', '')
        try:
            req.save()
            req.send_confirmation_email()
        except model.MoneyOutRequest.NotEnoughMoney:
            return h.JSON({'error': True,
                           'msg': u'Недостаточно средств для вывода!',
                           'ok': False})
        except model.MoneyOutRequest.NotConfirm:
            return h.JSON({'error': True,
                           'msg': u'Сушествуют необработанные заявки. Дождитесь ихней обработки.',
                           'ok': False})
        except Exception as ex:
            log.debug(repr(ex))
        return h.JSON({'error': False,
           'ok': True,
           'msg': u'Заявка успешно принята'})
    
    def _moneyOutSubmit_card_pb_us(self):
        ''' Обработка заявки на вывод средств посредством пластиковой карты '''
        schema = MoneyOutForm_card_pb_us()
        try:
            form = schema.to_python(dict(request.params))
        except formencode.Invalid, error:
            errorMessage = '<br/>\n'.join(
                            [x.msg for x in error.error_dict.values()])
            return h.JSON({'error': True, 'msg': errorMessage, 'ok': False})

        req = model.CardMoneyOutRequest_pb_us()
        req.account = model.Account(c.user)
        req.ip = request.environ['REMOTE_ADDR']
        req.summ = form.get('moneyOut_cardSumm_pb_us', '')
        req.comment = form.get('moneyOut_cardComment_pb_us', '')
        req.card_number = form.get('moneyOut_cardNumber_pb_us', '')
        req.card_name = form.get('moneyOut_cardName_pb_us', '')
        req.card_type = form.get('moneyOut_cardType_pb_us', '')
        req.card_currency = form.get('moneyOut_cardCurrency_pb_us')
        req.expire_year = form.get('moneyOut_cardYear_pb_us', '')
        req.expire_month = form.get('moneyOut_cardMonth_pb_us', '')
        req.card_phone = form.get('moneyOut_cardPhone_pb_us', '')
        try:
            req.save()
            req.send_confirmation_email()
        except model.MoneyOutRequest.NotEnoughMoney:
            return h.JSON({'error': True,
                           'msg': u'Недостаточно средств для вывода!',
                           'ok': False})
        except model.MoneyOutRequest.NotConfirm:
            return h.JSON({'error': True,
                           'msg': u'Сушествуют необработанные заявки. Дождитесь ихней обработки.',
                           'ok': False})
        except Exception as ex:
            log.debug(repr(ex))
        return h.JSON({'error': False,
           'ok': True,
           'msg': u'Заявка успешно принята'})

    def _moneyOutSubmit_cash(self):
        ''' Обработка заявки на вывод средств посредством пластиковой карты '''
        schema = MoneyOutForm_cash()
        try:
            form = schema.to_python(dict(request.params))
        except formencode.Invalid, error:
            errorMessage = '<br/>\n'.join(
                            [x.msg for x in error.error_dict.values()])
            return h.JSON({'error': True, 'msg': errorMessage, 'ok': False})

        req = model.CashMoneyOutRequest()
        req.account = model.Account(c.user)
        req.ip = request.environ['REMOTE_ADDR']
        req.summ = form.get('moneyOut_cashSumm', '')
        req.comment = form.get('moneyOut_cashComment', '')
        req.phone = form.get('moneyOut_cashPhone', '')
        try:
            req.save()
            req.send_confirmation_email()
        except model.MoneyOutRequest.NotEnoughMoney:
            return h.JSON({'error': True,
                           'msg': u'Недостаточно средств для вывода!',
                           'ok': False})
        except model.MoneyOutRequest.NotConfirm:
            return h.JSON({'error': True,
                           'msg': u'Сушествуют необработанные заявки. Дождитесь ихней обработки.',
                           'ok': False})
        except Exception as ex:
            log.debug(repr(ex))
        return h.JSON({'error': False,
           'ok': True,
           'msg': u'Заявка успешно принята'})


    def _moneyOutSubmit_factura(self):
        ''' Обработка заявки на вывод средств посредством счёт-фактуры '''
        schema = MoneyOutForm_factura()
        if not session.get('factura_file_name'):
            return h.JSON({'error': True,
                           'msg': u'Не загружен файл счёт-фактуры!',
                           'ok': False})
        try:
            form = schema.to_python(dict(request.params))
        except formencode.Invalid as error:
            errorMessage = '<br/>\n'.join(
                                [x.msg for x in error.error_dict.values()])
            return h.JSON({'error': True, 'msg': errorMessage, 'ok': False})

        req = model.InvoiceMoneyOutRequest()
        req.account = model.Account(c.user)
        req.ip = request.environ['REMOTE_ADDR']
        req.summ = form.get('moneyOut_facturaSumm')
        req.contacts = form.get('moneyOut_facturaContact')
        req.phone = form.get('moneyOut_facturaPhone')
        req.invoice_filename = session.get('factura_file_name')
        req.comment = form.get('moneyOut_facturaComment', '')
        try:
            req.save()
            req.send_confirmation_email()
        except model.MoneyOutRequest.NotEnoughMoney:
            return h.JSON({'error': True,
                           'msg': u'Недостаточно средств для вывода!',
                           'ok': False})
        except model.MoneyOutRequest.NotConfirm:
            return h.JSON({'error': True,
                           'msg': u'Сушествуют необработанные заявки. Дождитесь ихней обработки.',
                           'ok': False})
        except Exception as ex:
            log.debug(unicode(ex))
        return h.JSON({'error': False,
           'ok': True,
           'msg': u'Заявка успешно принята'})

    @current_user_check
    @expandtoken
    @authcheck
    def moneyOutRemove(self):
        ''' Отмена заявки на вывод средств'''
        try:
            id = int(request.params.get('id'))
            obj = app_globals.db.money_out_request \
                    .find({'user.login': c.user}) \
                    .sort('date', pymongo.DESCENDING)[id - 1]
            if obj.get('approved', False):
                return h.JSON({'error': True,
                               'msg': u'Эта заявка уже была выполнена'})
            app_globals.db.money_out_request.remove(obj, safe=True)
        except Exception as e:
            print e
            return h.JSON({'error': True, 'ok': False})
        return h.JSON({'error': False, 'ok': True,
                       'msg': u'Заявка успешно отменена'})

    @current_user_check
    @expandtoken
    @authcheck
    def register_domain_request(self):
        ''' Добавление заявки на регистрацию домена'''
        try:
            schema = RegisterDomainRequestForm()
            form = schema.to_python(dict(request.params))
            domain = form['txtRegisterDomainUrl']
            account = Account(login=c.user)
            account.domains.add_request(domain)
        except formencode.Invalid, error:
            errorMessage = '<br/>\n'.join(
                                    [x.msg for x in error.error_dict.values()])
            return h.JSON({'error': True, 'msg': errorMessage})
        except Account.Domains.AlreadyExistsError:
            return h.JSON({'error': True,
                           'msg': u"Данный домен уже был зарегистрирован"})
        except:
            raise
            return h.JSON({'error': True})
        else:
            return h.JSON({'error': False})
    
    @current_user_check
    @expandtoken
    @authcheck
    def remove_domain_request(self):
        ''' Добавление заявки на регистрацию домена'''
        try:
            schema = RemoveDomainRequestForm()
            form = schema.to_python(dict(request.params))
            domain = form['remove_domain']
            account = Account(login=c.user)
            account.domains.remove(domain)
        except formencode.Invalid, error:
            errorMessage = '<br/>\n'.join(
                                    [x.msg for x in error.error_dict.values()])
            return h.JSON({'error': True, 'msg': errorMessage})
        except Exception as e :
            raise
            return h.JSON({'error': True, 'msg': e})
        else:
            return h.JSON({'error': False})

    def confirmRequestToApproveMoneyOut(self, id):
        ''' Подтверждение заявки на вывод средств по выданной ссылке '''
        try:
            c.text_message = u''
            money_out_request = \
                app_globals.db.money_out_request.find_one({'confirm_guid': id})

            if not money_out_request:
                raise UserWarning(u'''
                    <h2>Заявки не существует</h2>
                    <p>Возможно, Вы уже отозвали данную заявку на вывод 
                    средств</p>''')

            if money_out_request['date'] - datetime.today() > \
                                                        timedelta(days=3):
                raise UserWarning(u'''
                    <h2>Извините! Ваша заявка устарела.</h2>
                    <p>Пожалуйста, оформите новую заявку в личном кабинете.
                    </p>''')

            if money_out_request.get('user_confirmed'):
                raise UserWarning(u'''
                    <h2>Заявка уже была подтверждена!</h2>''')

            money_out_request['user_confirmed'] = True
            app_globals.db.money_out_request.save(money_out_request, safe=True)

        except UserWarning as ex:
            c.text_message = unicode(ex)

        except Exception as ex:
            c.text_message = u'''
                <h2>Произошла ошибка! </h2>
                <p> Заявка не была подтверждена. Пожалуйста, свяжитесь с
                    вашим менеджером!</p>
                <p>Техническая информация: %s.</p>''' % str(ex)
        else:
            c.text_message = u'''
                <h2> Заявка подтверждена.</h2>
                <p>Спасибо за участие в программе GetMyAd!</p>'''

        footer = u"""
            <br/><p style="font-style:italic;">С уважением,<br/>
            Отдел Развития Рекламной Сети Yottos GetMyAd.<br/>
            partner@yottos.com<br/>
            тел.: +38 (050) 406 20 20.</p>"""
        c.text_message = c.text_message + footer
        return render('/thanks_user_confirm.mako.html')

    @current_user_check
    def removeUploadFactura(self):
        try:
            filename = session.get('factura_file_name')
            os.remove('%s/%s' % (config.get('schet_factura_folder'), filename))
            session['factura_file_name'] = ''
            session.save()
        except:
            return h.JSON({'error': True, 'msg': u'Ошибка удаления файла!'})
        return h.JSON({'error': False})

    @current_user_check
    def uploadFactura(self):
        try:
            form = request.params.get("userfile")
            file_guid = str(uuid1().hex).upper()
            extension = os.path.splitext(form.filename)[-1]
            filename = file_guid + extension
            location = '%s/%s' % (config.get('schet_factura_folder'), filename)
            dir = os.path.dirname(location)
            if not os.path.exists(dir):
                os.mkdir(dir)
            file_on_server = open(location, 'w')
            file_on_server.write(form.value)
            file_on_server.close()
            session['factura_file_name'] = filename
            session.save()
        except:
            return h.JSON({'error': True})
        return h.JSON({'error': False})

    @current_user_check
    def lastMoneyOutDetails(self):
        ''' Подробные данные о последней заявке на вывод средств '''
        try:
            data = AccountReports(Account(c.user)).money_out_requests()
            if not data:
                return h.JSON({})
            data.sort(key=lambda x: x['date'], reverse=True)
            return h.JSON(data[0])
        except Exception as ex:
            return h.JSON({'error': True, 'ok': False, 'msg': unicode(ex)})


class MoneyOutForm_web(formencode.Schema):
    """Форма вывода денег на web money"""
    allow_extra_fields = True
    filter_extra_fields = True
    moneyOut_summ = \
        v.Number(min=10, not_empty=True,
                 messages={'empty': u'Пожалуйста, введите сумму!',
                           'number': u'Пожалуйста, введите корректную сумму!',
                           'tooLow': u'Сумма должна быть не менее %(min)s грн!'})
    moneyOut_webmoneyLogin = \
        v.Regex(regex='^[0-9]{12}$', not_empty=True,
                messages={'empty': u'Пожалуйста, введите WMID!',
                          'invalid': u'WMID должен состоять из 12 цифр!'})
    moneyOut_webmoneyAccountNumber = \
        v.Regex(regex='^[Zz][0-9]{12}$', not_empty=True,
                messages={
                    'empty': u'Пожалуйста, введите номер кошелька WebMoney!',
                    'invalid': u'Номер кошелька состоит из Z и 12 цифр!'})
    moneyOut_phone = \
        v.NotEmpty(messages={'empty': u'Пожалуйста, введите номер телефона!'})
    moneyOut_comment = \
        v.String(if_missing=None)

class MoneyOutForm_web_r(formencode.Schema):
    """Форма вывода денег на web money"""
    allow_extra_fields = True
    filter_extra_fields = True
    moneyOut_summ_r = \
        v.Number(min=10, not_empty=True,
                 messages={'empty': u'Пожалуйста, введите сумму!',
                           'number': u'Пожалуйста, введите корректную сумму!',
                           'tooLow': u'Сумма должна быть не менее %(min)s грн!'})
    moneyOut_webmoneyLogin_r = \
        v.Regex(regex='^[0-9]{12}$', not_empty=True,
                messages={'empty': u'Пожалуйста, введите WMID!',
                          'invalid': u'WMID должен состоять из 12 цифр!'})
    moneyOut_webmoneyAccountNumber_r = \
        v.Regex(regex='^[Rr][0-9]{12}$', not_empty=True,
                messages={
                    'empty': u'Пожалуйста, введите номер кошелька WebMoney!',
                    'invalid': u'Номер кошелька состоит из r и 12 цифр!'})
    moneyOut_phone_r = \
        v.NotEmpty(messages={'empty': u'Пожалуйста, введите номер телефона!'})
    moneyOut_comment_r = \
        v.String(if_missing=None)

class MoneyOutForm_web_u(formencode.Schema):
    """Форма вывода денег на web money"""
    allow_extra_fields = True
    filter_extra_fields = True
    moneyOut_summ_u = \
        v.Number(min=10, not_empty=True,
                 messages={'empty': u'Пожалуйста, введите сумму!',
                           'number': u'Пожалуйста, введите корректную сумму!',
                           'tooLow': u'Сумма должна быть не менее %(min)s грн!'})
    moneyOut_webmoneyLogin_u = \
        v.Regex(regex='^[0-9]{12}$', not_empty=True,
                messages={'empty': u'Пожалуйста, введите WMID!',
                          'invalid': u'WMID должен состоять из 12 цифр!'})
    moneyOut_webmoneyAccountNumber_u = \
        v.Regex(regex='^[Uu][0-9]{12}$', not_empty=True,
                messages={
                    'empty': u'Пожалуйста, введите номер кошелька WebMoney!',
                    'invalid': u'Номер кошелька состоит из U и 12 цифр!'})
    moneyOut_phone_u = \
        v.NotEmpty(messages={'empty': u'Пожалуйста, введите номер телефона!'})
    moneyOut_comment_u = \
        v.String(if_missing=None)

class MoneyOutForm_yandex(formencode.Schema):
    """Форма вывода денег на web money"""
    allow_extra_fields = True
    filter_extra_fields = True
    moneyOut_yandexSumm = \
        v.Number(min=10, not_empty=True,
                 messages={'empty': u'Пожалуйста, введите сумму!',
                           'number': u'Пожалуйста, введите корректную сумму!',
                           'tooLow': u'Сумма должна быть не менее %(min)s грн!'})
    moneyOut_yandex_number = \
        v.Regex(regex='^[0-9]{1,20}$', not_empty=True,
                messages={
                    'empty': u'Пожалуйста, введите номер счёта Яндекс Деньги!',
                    'invalid': u'Номер счёта должен содержать до 20 цифр!'})
    moneyOut_yandex_phone = \
        v.NotEmpty(messages={'empty': u'Пожалуйста, введите номер телефона!'})
    moneyOut_yandex_comment = \
        v.String(if_missing=None)

class MoneyOutForm_card(formencode.Schema):
    """Форма вывода денег на пластиковую карту"""
    allow_extra_fields = True
    filter_extra_fields = True
    moneyOut_cardSumm = \
        v.Number(min=10, not_empty=True,
                 messages={'empty': u'Пожалуйста, введите сумму!',
                           'number': u'Пожалуйста, введите корректную сумму!',
                           'tooLow': u'Сумма должна быть не менее %(min)s грн!'})
    moneyOut_cardName = \
        v.Regex(regex='([^\s]+)\s+([^\s]+)\s+([^\s]+)+', not_empty=True,
                messages={
                    'empty': u'Пожалуйста, введите Ф.И.О владельца карты!',
                    'invalid': u'Введите полностью Фамилию Имя Отчество'})
    moneyOut_cardNumber = \
        v.Regex(regex='^(\d{4}[ -]?){3}\d{4}$', not_empty=True,
                messages={
                    'empty': u'Пожалуйста, укажите номер пластиковой карты!',
                    'invalid': u'Номер карты должен состоять из 16 цифр!'})
    moneyOut_cardMonth = \
        v.NotEmpty(
            messages={'empty': u'Пожалуйста, укажите месяц до которого '
                               u'возможно использование пластиковой карты!'})
    moneyOut_cardYear = \
        v.NotEmpty(
            messages={
                'empty': u'Пожалуйста, укажите год до которго возможно '
                         u'использование пластиковой карты!'})
    moneyOut_cardBank = \
        v.NotEmpty(
            messages={'empty': u'Пожалуйста, укажите название банка!'})
    moneyOut_cardType = \
        v.String(if_missing=None)
    moneyOut_cardPhone = \
        v.NotEmpty(
            messages={'empty': u'Пожалуйста, укажите контактный телефон!'})
    moneyOut_cardComment = \
        v.String(if_missing=None)
    moneyOut_cardCurrency = \
        v.String(if_missing=None)
    moneyOut_cardBankMFO = \
        v.Regex(
            regex="^\d{6}$",
            messages={'invalid': u'МФО банка должен состоять из 6 цифр!'})
    moneyOut_cardBankOKPO = \
        v.Regex(
            regex="[0-9]+",
            messages={'invalid': u'ОКПО банка должен состоять из  цифр!'})
    moneyOut_cardBankTransitAccount = \
        v.Regex(
           regex="[0-9]+",
           messages={'invalid': u'Транзитый счёт должен состоять из  цифр!'})

class MoneyOutForm_card_pb_ua(formencode.Schema):
    """Форма вывода денег на пластиковую карту"""
    allow_extra_fields = True
    filter_extra_fields = True
    moneyOut_cardSumm_pb_ua = \
        v.Number(min=10, not_empty=True,
                 messages={'empty': u'Пожалуйста, введите сумму!',
                           'number': u'Пожалуйста, введите корректную сумму!',
                           'tooLow': u'Сумма должна быть не менее %(min)s грн!'})
    moneyOut_cardName_pb_ua = \
        v.Regex(regex='([^\s]+)\s+([^\s]+)\s+([^\s]+)+', not_empty=True,
                messages={
                    'empty': u'Пожалуйста, введите Ф.И.О владельца карты!',
                    'invalid': u'Введите полностью Фамилию Имя Отчество'})
    moneyOut_cardNumber_pb_ua = \
        v.Regex(regex='^(\d{4}[ -]?){3}\d{4}$', not_empty=True,
                messages={
                    'empty': u'Пожалуйста, укажите номер пластиковой карты!',
                    'invalid': u'Номер карты должен состоять из 16 цифр!'})
    moneyOut_cardMonth_pb_ua = \
        v.NotEmpty(
            messages={'empty': u'Пожалуйста, укажите месяц до которого '
                               u'возможно использование пластиковой карты!'})
    moneyOut_cardYear_pb_ua = \
        v.NotEmpty(
            messages={
                'empty': u'Пожалуйста, укажите год до которго возможно '
                         u'использование пластиковой карты!'})
    moneyOut_cardType_pb_ua = \
        v.String(if_missing=None)
    moneyOut_cardPhone_pb_ua = \
        v.NotEmpty(
            messages={'empty': u'Пожалуйста, укажите контактный телефон!'})
    moneyOut_cardComment_pb_ua = \
        v.String(if_missing=None)
    moneyOut_cardCurrency_pb_ua = \
        v.String(if_missing=None)

class MoneyOutForm_card_pb_us(formencode.Schema):
    """Форма вывода денег на пластиковую карту"""
    allow_extra_fields = True
    filter_extra_fields = True
    moneyOut_cardSumm_pb_us = \
        v.Number(min=10, not_empty=True,
                 messages={'empty': u'Пожалуйста, введите сумму!',
                           'number': u'Пожалуйста, введите корректную сумму!',
                           'tooLow': u'Сумма должна быть не менее %(min)s грн!'})
    moneyOut_cardName_pb_us = \
        v.Regex(regex='([^\s]+)\s+([^\s]+)\s+([^\s]+)+', not_empty=True,
                messages={
                    'empty': u'Пожалуйста, введите Ф.И.О владельца карты!',
                    'invalid': u'Введите полностью Фамилию Имя Отчество'})
    moneyOut_cardNumber_pb_us = \
        v.Regex(regex='^(\d{4}[ -]?){3}\d{4}$', not_empty=True,
                messages={
                    'empty': u'Пожалуйста, укажите номер пластиковой карты!',
                    'invalid': u'Номер карты должен состоять из 16 цифр!'})
    moneyOut_cardMonth_pb_us = \
        v.NotEmpty(
            messages={'empty': u'Пожалуйста, укажите месяц до которого '
                               u'возможно использование пластиковой карты!'})
    moneyOut_cardYear_pb_us = \
        v.NotEmpty(
            messages={
                'empty': u'Пожалуйста, укажите год до которго возможно '
                         u'использование пластиковой карты!'})
    moneyOut_cardType_pb_us = \
        v.String(if_missing=None)
    moneyOut_cardPhone_pb_us = \
        v.NotEmpty(
            messages={'empty': u'Пожалуйста, укажите контактный телефон!'})
    moneyOut_cardComment_pb_us = \
        v.String(if_missing=None)
    moneyOut_cardCurrency_pb_us = \
        v.String(if_missing=None)

class MoneyOutForm_cash(formencode.Schema):
    """Форма вывода денег на пластиковую карту"""
    allow_extra_fields = True
    filter_extra_fields = True
    moneyOut_cashSumm = \
        v.Number(min=10, not_empty=True,
                 messages={'empty': u'Пожалуйста, введите сумму!',
                           'number': u'Пожалуйста, введите корректную сумму!',
                           'tooLow': u'Сумма должна быть не менее %(min)s грн!'})
    moneyOut_cashPhone = \
        v.NotEmpty(
            messages={'empty': u'Пожалуйста, укажите контактный телефон!'})
    moneyOut_cashComment = \
        v.String(if_missing=None)


class MoneyOutForm_factura(formencode.Schema):
    """Форма вывода денег на пластиковую карту"""
    allow_extra_fields = True
    filter_extra_fields = True
    moneyOut_facturaSumm = \
        v.Number(
            min=10,
            not_empty=True,
            messages={'empty': u'Укажите сумму вывода!',
                      'number': u'Укажите корректную сумму!',
                      'tooLow': u'Сумма должна быть не менее %(min)s грн!'})
    moneyOut_facturaContact = \
        v.NotEmpty(
            messages={'empty': u'Пожалуйста, укажите контактное лицо!'})
    moneyOut_facturaPhone = \
        v.NotEmpty(
            messages={'empty': u'Пожалуйста, укажите номер телефона!'})
    moneyOut_facturaComment = \
        v.String(if_missing=None)


class RegisterDomainRequestForm(formencode.Schema):
    ''' Форма заявки на регистрацию домена '''
    allow_extra_fields = True
    filter_extra_fields = True
    txtRegisterDomainUrl = \
        v.URL(
            add_http=True,
            check_exists=True,
            allow_idna=True,
            not_empty=True,
            messages={'badURL': u'Неверный формат ссылки!',
                      'notFound': u'Указанный сайт не найден!',
                      'noTLD': u'Вы должны указать полное доменное имя '
                               u'(например, %(domain)s.com)',
                      'httpError': u'Во время попытки обращения к данному '
                                   u'сайту возникла ошибка: %(error)s',
                      'status': u'Во время попытки обращения к данному '
                                   u'сайту возникла ошибка: %(status)s',
                      'socketError': u'Во время попытки обращения к серверу '
                                     u'возникла ошибка: %(error)s',
                      'empty': u'Пожалуйста, введите url сайта!'
                      })

class RemoveDomainRequestForm(formencode.Schema):
    ''' Форма заявки на регистрацию домена '''
    allow_extra_fields = True
    filter_extra_fields = True
    remove_domain = \
        v.URL(
            add_http=True,
            check_exists=False,
            allow_idna=True,
            not_empty=True,
            messages={'badURL': u'Неверный формат ссылки!',
                      'notFound': u'Указанный сайт не найден!',
                      'noTLD': u'Вы должны указать полное доменное имя '
                               u'(например, %(domain)s.com)',
                      'httpError': u'Во время попытки обращения к данному '
                                   u'сайту возникла ошибка: %(error)s',
                      'status': u'Во время попытки обращения к данному '
                                   u'сайту возникла ошибка: %(status)s',
                      'socketError': u'Во время попытки обращения к серверу '
                                     u'возникла ошибка: %(error)s',
                      'empty': u'Пожалуйста, введите url сайта!'
                      })
