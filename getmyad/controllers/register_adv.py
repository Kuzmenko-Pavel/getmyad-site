# -*- coding: UTF-8 -*-
import logging

from formencode import Schema
from getmyad.lib import helpers as h
from getmyad.lib.base import BaseController, render
from getmyad.model import Account, Permission
from pylons import request, session, tmpl_context as c, app_globals
import formencode

log = logging.getLogger(__name__)


class RegisterAdvController(BaseController):
    def __init__(self):
        c.name = ''
        c.phone = ''
        c.email = ''
        c.skype = ''
        c.siteUrl = ''
        c.user_error_messages = ''
        c.manager_error_messages = ''
        c.login = ''
        c.password = ''
        c.minsum = ''
        c.manager_get = ''
        c.list_manager = []
        c.manager_name = ''
        c.manager_login = ''
        c.manager_phone = ''
        c.manager_email = ''
        c.manager_skype = ''
        c.account_type = ''
        c.click_percent = 50
        c.click_cost_min = 0.01
        c.click_cost_max = 1.00
        c.imp_percent = 50
        c.imp_cost_min = 0.05
        c.imp_cost_max = 2.00
        c.range_short_term = 100
        c.range_long_term = 0
        c.range_context = 0
        c.range_search = 100
        c.range_retargeting = 33
        c.money_cash = False
        c.money_web_z = False
        c.money_web_r = False
        c.money_web_u = False
        c.money_card = False
        c.money_card_pb_ua = False
        c.money_card_pb_us = False
        c.money_factura = False
        c.money_yandex = False
        c.list_manager = Account.active_managers()
        c.categories = [[x['guid'], x['title']] for x in app_globals.db.advertise.category.find()]

    def __before__(self, action, **params):
        user = session.get('user')
        if user and session.get('isManager', False):
            self.user = user
            request.environ['CURRENT_USER'] = user
            request.environ['IS_MANAGER'] = True
        else:
            self.user = ''

    def index(self):
        if not self.user: return h.userNotAuthorizedError()
        permission = Permission(Account(login=self.user))
        if not permission.has(Permission.REGISTER_USERS_ACCOUNT):
            return h.userNotAuthorizedError()
        return render('/register_adv.mako.html')

    class PaymentTypeNotDefined(Exception):
        ''' Не выбран ни один способ вывода средств '''

        def __init__(self, value):
            self.value = value

        def __str__(self):
            return 'PaymentTypeNotDefined'

    def createUser(self):
        """Создаёт пользователя GetMyAd"""
        if not self.user: return h.userNotAuthorizedError()
        c.account_type = request.params.get('account_type', 'user')
        if c.account_type == 'user':
            schema = RegisterUserForm()
            try:
                form_result = schema.to_python(dict(request.params))
                c.name = form_result['name']
                c.phone = form_result['phone']
                c.email = form_result['email']
                c.skype = form_result['skype']
                c.siteUrl = form_result['siteUrl']
                c.minsum = request.params.get('minsum')
                c.click_percent = form_result['click_percent']
                c.click_cost_min = form_result['click_cost_min']
                c.click_cost_max = form_result['click_cost_max']
                c.imp_percent = form_result['imp_percent']
                c.imp_cost_min = form_result['imp_cost_min']
                c.imp_cost_max = form_result['imp_cost_max']
                c.range_short_term = form_result['range_short_term']
                c.range_long_term = form_result['range_long_term']
                c.range_context = form_result['range_context']
                c.range_search = form_result['range_search']
                c.range_retargeting = form_result['range_retargeting']
                c.manager_get = request.params.get('manager_get')
                c.money_cash = False if request.params.get('money_cash') == None else True
                c.money_card = False if request.params.get('money_card') == None else True
                c.money_card_pb_ua = False if request.params.get('money_card_pb_ua') == None else True
                c.money_card_pb_us = False if request.params.get('money_card_pb_us') == None else True
                c.money_web_z = False if request.params.get('money_web_z') == None else True
                c.money_web_r = False if request.params.get('money_web_r') == None else True
                c.money_web_u = False if request.params.get('money_web_u') == None else True
                c.money_factura = False if request.params.get('money_factura') == None else True
                c.money_yandex = False if request.params.get('money_yandex') == None else True
                c.category = request.params.getall('categories')
                if (not c.money_card
                    and not c.money_web_z
                    and not c.money_factura
                    and not c.money_cash
                    and not c.money_card_pb_ua
                    and not c.money_card_pb_us
                    and not c.money_web_r
                    and not c.money_web_u
                    and not c.money_yandex):
                    raise RegisterAdvController.PaymentTypeNotDefined('Payment_type_not_defined')
            except formencode.Invalid, error:
                c.user_error_messages = '<br/>\n'.join([x.msg for x in error.error_dict.values()])
                c.siteUrl = request.params.get('siteUrl')
                c.name = request.params.get('name')
                c.phone = request.params.get('phone')
                c.email = request.params.get('email')
                c.skype = request.params.get('skype')
                c.minsum = request.params.get('minsum')
                c.click_percent = request.params.get('click_percent')
                c.click_cost_min = request.params.get('click_cost_min')
                c.click_cost_max = request.params.get('click_cost_max')
                c.imp_percent = request.params.get('imp_percent')
                c.imp_cost_min = request.params.get('imp_cost_min')
                c.imp_cost_max = request.params.get('imp_cost_max')
                c.range_short_term = request.params.get('range_short_term')
                c.range_long_term = request.params.get('range_long_term')
                c.range_context = request.params.get('range_context')
                c.range_search = request.params.get('range_search')
                c.range_retargeting = request.params.get('range_retargeting')
                c.manager_get = request.params.get('manager_get')
                c.money_cash = False if request.params.get('money_cash') == None else True
                c.money_card = False if request.params.get('money_card') == None else True
                c.money_card_pb_ua = False if request.params.get('money_card_pb_ua') == None else True
                c.money_card_pb_us = False if request.params.get('money_card_pb_us') == None else True
                c.money_web_z = False if request.params.get('money_web_z') == None else True
                c.money_web_r = False if request.params.get('money_web_r') == None else True
                c.money_web_u = False if request.params.get('money_web_u') == None else True
                c.money_factura = False if request.params.get('money_factura') == None else True
                c.money_yandex = False if request.params.get('money_yandex') == None else True
                c.category = request.params.getall('categories')
                return self.index()
            except self.PaymentTypeNotDefined:
                c.user_error_messages = u'Укажите хотя бы один способ вывода средств'
                return self.index()

            c.siteUrl = request.params.get('siteUrl')
            if c.siteUrl.startswith('http://www.'):
                c.siteUrl = c.siteUrl[11:]
            elif c.siteUrl.startswith('http://'):
                c.siteUrl = c.siteUrl[7:]
            elif c.siteUrl.startswith('https://'):
                c.siteUrl = c.siteUrl[8:]
            elif c.siteUrl.startswith('www.'):
                c.siteUrl = c.siteUrl[4:]
            c.siteUrl = c.siteUrl.split('/')[0]

            c.money_out = ''
            if c.money_cash:
                c.money_out += u'наличный расчет'
            if c.money_card:
                c.money_out += u'банковская платёжная карта'
            if c.money_card_pb_ua:
                c.money_out += u'ПриватБанковская платёжная карта UAH'
            if c.money_card_pb_us:
                c.money_out += u'ПриватБанковская платёжная карта USD'
            if c.money_web_z:
                if len(c.money_out):
                    c.money_out += ', '
                c.money_out += u'webmoney_z'
            if c.money_web_r:
                if len(c.money_out):
                    c.money_out += ', '
                c.money_out += u'webmoney_r'
            if c.money_web_u:
                if len(c.money_out):
                    c.money_out += ', '
                c.money_out += u'webmoney_u'
            if c.money_factura:
                if len(c.money_out):
                    c.money_out += ', '
                c.money_out += u'счёт фактура'
            if c.money_yandex:
                if len(c.money_out):
                    c.money_out += ', '
                c.money_out += u'yandex'

        else:
            schema = RegisterManagerForm()
            try:
                form_result = schema.to_python(dict(request.params))
                c.manager_login = form_result['manager_login']
                c.manager_name = form_result['manager_name']
                c.manager_email = form_result['manager_email']
                c.manager_skype = form_result['manager_skype']
                c.manager_phone = form_result['manager_phone']
            except formencode.Invalid, error:
                c.manager_error_messages = '<br/>\n'.join([x.msg for x in error.error_dict.values()])
                c.manager_login = request.params.get('manager_login')
                c.manager_name = request.params.get('manager_name')
                c.manager_email = request.params.get('manager_email')
                c.manager_skype = request.params.get('manager_skype')
                c.manager_phone = request.params.get('manager_phone')
                return self.index()

        c.user_error_messages = c.manager_error_messages = ''
        c.save_res = self.saveUser()
        if not c.save_res[0]:
            c.user_error_messages = c.save_res[1]
            return self.index()
        return render("/register.thanks.mako.html")

    def saveUser(self):
        ''' Сохраняет создаваемый аккаунт в бд'''
        try:
            if c.account_type == 'user':
                account = Account(login=c.siteUrl)
                if account.domains.check_exists(c.siteUrl):
                    return (False, "Данный сайт уже зарегестрирован")
                account.email = c.email
                account.skype = c.skype
                account.phone = c.phone
                account.owner_name = c.name
                account.min_out_sum = c.minsum
                account.manager_get = c.manager_get
                account.money_web_z = c.money_web_z
                account.money_web_r = c.money_web_r
                account.money_web_u = c.money_web_u
                account.money_card = c.money_card
                account.money_cash = c.money_cash
                account.money_card_pb_ua = c.money_card_pb_ua
                account.money_card_pb_us = c.money_card_pb_us
                account.money_factura = c.money_factura
                account.money_yandex = c.money_yandex
                account.click_percent = c.click_percent
                account.click_cost_min = c.click_cost_min
                account.click_cost_max = c.click_cost_max
                account.imp_percent = c.imp_percent
                account.imp_cost_min = c.imp_cost_min
                account.imp_cost_max = c.imp_cost_max
                account.range_short_term = (int(c.range_short_term) / 100.0)
                account.range_long_term = (int(c.range_long_term) / 100.0)
                account.range_context = (int(c.range_context) / 100.0)
                account.range_search = (int(c.range_search) / 100.0)
                account.range_retargeting = (int(c.range_retargeting) / 100.0)
            else:
                account = Account(login=c.manager_login)
                account.email = c.manager_email
                account.skype = c.manager_skype
                account.phone = c.manager_phone
                account.owner_name = c.manager_name

            account.password = Account.makePassword()
            c.password = account.password
            account.account_type = {'user': Account.User,
                                    'manager': Account.Manager,
                                    'admin': Account.Administrator
                                    }.get(c.account_type, Account.User)
            account.register()
            if c.account_type == 'user':
                account.domains.add(account.login)
                account.domains.categories_add(account.login, c.category)
        except Exception as e:
            print e
            return (False, e)
        return (True, '')


class RegisterUserForm(Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    siteUrl = formencode.validators.URL(
        not_empty=True,
        messages={'badURL': u'Неправильный формат URL',
                  'empty': u'Введите URL'})
    name = formencode.validators.String(
        not_empty=True,
        messages={'empty': u'Введите ФИО'})
    phone = formencode.validators.String(
        not_empty=True,
        messages={'empty': u'Введите телефон'})
    click_percent = formencode.validators.Number(
        not_empty=True,
        messages={'empty': u'Введите процент от цены рекламодателя',
                  'number': u'Некорректный формат числа'})
    click_cost_min = formencode.validators.Number(
        not_empty=True,
        messages={'empty': u'Введите минимальную цену за клик',
                  'number': u'Некорректный формат числа'})
    click_cost_max = formencode.validators.Number(
        not_empty=True,
        messages={'empty': u'Введите максимальную цену за клик',
                  'number': u'Некорректный формат числа'})
    imp_percent = formencode.validators.Number(
        not_empty=True,
        messages={'empty': u'Введите процент от цены рекламодателя',
                  'number': u'Некорректный формат числа'})
    imp_cost_min = formencode.validators.Number(
        not_empty=True,
        messages={'empty': u'Введите минимальную цену за 1000 показов',
                  'number': u'Некорректный формат числа'})
    imp_cost_max = formencode.validators.Number(
        not_empty=True,
        messages={'empty': u'Введите максимальную цену за 1000 показов',
                  'number': u'Некорректный формат числа'})
    email = formencode.validators.Email(
        not_empty=True,
        messages={'empty': u'Введите e-mail',
                  'noAt': u'Неправильный формат e-mail',
                  'badUsername': u'Неправильный формат e-mail',
                  'badDomain': u'Неправильный формат e-mail'})
    skype = formencode.validators.String(
        not_empty=False,
        messages={'empty': u'Введите Skype'})
    range_retargeting = formencode.validators.Int(
        min=0,
        max=100,
        not_empty=True,
        messages={'empty': u'Введите вес ветки ретаргетинга',
                  'tooHigh': u'Пожалуйста, введите число, которое %(max)s меньше',
                  'tooLow': u'Пожалуйста, введите число, которое %(min)s больше',
                  'number': u'Некорректный формат числа'})
    range_search = formencode.validators.Int(
        not_empty=True,
        min=0,
        max=100,
        messages={'empty': u'Введите вес ветки поиска',
                  'tooHigh': u'Пожалуйста, введите число, которое %(max)s меньше',
                  'tooLow': u'Пожалуйста, введите число, которое %(min)s больше',
                  'number': u'Некорректный формат числа'})
    range_short_term = formencode.validators.Int(
        not_empty=True,
        min=0,
        max=100,
        messages={'empty': u'Введите вес ветки краткосрочной',
                  'tooHigh': u'Пожалуйста, введите число, которое %(max)s меньше',
                  'tooLow': u'Пожалуйста, введите число, которое %(min)s больше',
                  'number': u'Некорректный формат числа'})
    range_long_term = formencode.validators.Int(
        not_empty=True,
        min=0,
        max=100,
        messages={'empty': u'Введите вес ветки долгосрочной истории',
                  'tooHigh': u'Пожалуйста, введите число, которое %(max)s меньше',
                  'tooLow': u'Пожалуйста, введите число, которое %(min)s больше',
                  'number': u'Некорректный формат числа'})
    range_context = formencode.validators.Int(
        not_empty=True,
        min=0,
        max=100,
        messages={'empty': u'Введите вес ветки контекста',
                  'tooHigh': u'Пожалуйста, введите число, которое %(max)s меньше',
                  'tooLow': u'Пожалуйста, введите число, которое %(min)s больше',
                  'number': u'Некорректный формат числа'})


class RegisterManagerForm(Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    manager_login = formencode.validators.String(not_empty=True, messages={'empty': u'Введите логин'})
    manager_name = formencode.validators.String(not_empty=True, messages={'empty': u'Введите ФИО'})
    manager_phone = formencode.validators.String(not_empty=True, messages={'empty': u'Введите телефон'})
    manager_email = formencode.validators.Email(not_empty=True, messages={'empty': u'Введите e-mail'})
    manager_skype = formencode.validators.String(not_empty=True, messages={'empty': u'Введите Skype'})
