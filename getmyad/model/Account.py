# -*- coding: UTF-8 -*-
import datetime
import logging
from uuid import uuid1

import pymongo
from pylons import app_globals

from getmyad.lib.helpers import uuid_to_long, formatMoney
from getmyad.model import mq
from getmyad.model.Informer import Informer

log = logging.getLogger(__name__)


class Account(object):
    """ Аккаунт пользователя """

    class AlreadyExistsError(Exception):
        ''' Попытка добавить существующий логин '''

        def __init__(self, login):
            self.login = login

        def __str__(self):
            return 'Account with login %s is already used' % self.login

    class NotFoundError(Exception):
        ''' Указанный аккаунт не найден '''

        def __init__(self, login):
            self.login = login

        def __str__(self):
            return 'Account %s not found' % self.login

    class UpdateError(Exception):
        ''' Ошибка обновления аккаунта'''

        def __init__(self, login):
            self.login = login

        def __str__(self):
            return 'Account %s was not updated' % self.login

    class Domains():
        ''' Работа с доменами пользователя '''

        class DomainAddError(Exception):
            def __init__(self, login):
                self.login = login

            def __str__(self):
                return 'Domain for login %s was not saved' % self.login

        class AlreadyExistsError(Exception):
            def __init__(self, domain):
                self.domain = domain

            def __str__(self):
                return 'Domain %s already exists' % self.domain

        def __init__(self, account):
            assert isinstance(account, Account), "'account' parameter should be an Account instance"
            self.account = account
            self.db = account.db
            self.db_m = account.db_m

        def __call__(self):
            return self.list()

        def list(self):
            """ Возвращает список доменов, назначенных данному аккаунту """
            data = self.db.domain.find_one({'login': self.account.login})
            try:
                domains = data['domains']
                assert isinstance(domains, dict)
                domains = [value for key, value in domains.items()]
                return domains
            except (AssertionError, KeyError, TypeError):
                return []

        def all_list(self):
            """ Возвращает список доменов, в системе """
            cursor = self.db.domain.find({})
            domains = []
            try:
                for data in cursor:
                    item = data['domains']
                    assert isinstance(item, dict)
                    domains += [value for key, value in item.iteritems()]
                return domains
            except (AssertionError, KeyError, TypeError):
                return domains

        def list_request(self):
            """ Возвращает список заявок на регистрацию домена данного аккаунта """
            data = self.db.domain.find_one({'login': self.account.login})
            try:
                requests = data['requests']
                assert isinstance(requests, list)
                return requests
            except (AssertionError, KeyError, TypeError):
                return []

        def add(self, url):
            """ Добавляет домен к списку разрешённых доменов пользователя """
            try:
                domain = url
                if domain.startswith('http://'):
                    domain = domain[7:]
                if domain.startswith('https://'):
                    domain = domain[8:]
                if domain.startswith('www.'):
                    domain = domain[4:]

                self.db.domain.update({'login': self.account.login},
                                      {'$set': {('domains.' + str(uuid1())): domain}},
                                      upsert=True)
                mq.MQ().account_update(self.account.login)
            except (pymongo.errors.OperationFailure):
                raise Account.Domains.DomainAddError(self.account.login)

        def categories_add(self, domain, categories):
            """ Добавляет домен к списку разрешённых доменов пользователя """
            try:
                self.db.domain.categories.update({'domain': domain},
                                                 {'$set':
                                                      {'categories': categories}
                                                  },
                                                 upsert=True)
                mq.MQ().account_update(self.account.login)
            except (pymongo.errors.OperationFailure):
                raise Account.Domains.DomainAddError(self.account.login)

        def list_requests(self):
            """ Возвращает список заявок на регистрацию доменов """
            data = self.db.domain.find_one({'login': self.account.login})
            try:
                requests = data['requests']
                assert isinstance(requests, list)
                return requests
            except (AssertionError, KeyError, TypeError):
                return []

        def check_exists(self, url):
            return filter(lambda x: x == url or ('http://%s' % x) == url or ('https://%s' % x) == url, self.all_list())

        def add_request(self, url):
            """ Добавляет заявку на добавление домена """
            domain = url
            if domain.startswith('http://'):
                domain = domain[7:]
            if domain.startswith('https://'):
                domain = domain[8:]
            if domain.startswith('www.'):
                domain = domain[4:]

            if filter(lambda x: x == domain or ('http://%s' % x) == domain or ('https://%s' % x) == domain,
                      self.all_list()):
                raise Account.Domains.AlreadyExistsError(self.account.login)

            self.db.domain.update({'login': self.account.login},
                                  {'$addToSet': {'requests': domain}}, upsert=True)

        def approve_request(self, url):
            """ Одобряет заявку на добавление домена """
            # Проверяем, была ли подана такая заявка
            domain = url
            if domain.startswith('http://'):
                domain = domain[7:]
            if domain.startswith('https://'):
                domain = domain[8:]
            if domain.startswith('www.'):
                domain = domain[4:]

            if not self.db.domain.find_one({'login': self.account.login, 'requests': domain}):
                return False
            self.add(domain)
            self.remove_request(domain)

        def remove_request(self, url):
            """ Удаляет заявку на добавление домена """
            domain = url
            if domain.startswith('http://'):
                domain = domain[7:]
            if domain.startswith('https://'):
                domain = domain[8:]
            if domain.startswith('www.'):
                domain = domain[4:]
            self.db.domain.update({'login': self.account.login},
                                  {'$pull': {'requests': domain}}, upsert=True)

        def reject_request(self, url):
            domain = url
            if domain.startswith('http://'):
                domain = domain[7:]
            if domain.startswith('https://'):
                domain = domain[8:]
            if domain.startswith('www.'):
                domain = domain[4:]
            if not self.db.domain.find_one({'login': self.account.login, 'requests': domain}):
                return False
            self.db.domain.update({'login': self.account.login},
                                  {'$addToSet': {'rejected': domain}}, upsert=True)
            self.remove_request(domain)

        def remove(self, url):
            domain = url
            if domain.startswith('http://'):
                domain = domain[7:]
            if domain.startswith('https://'):
                domain = domain[8:]
            if domain.startswith('www.'):
                domain = domain[4:]
            data = self.db.domain.find({'login': self.account.login})
            for item in data:
                domains = item.get('domains', {})
                for key, value in domains.items():
                    if value == domain or ('http://%s' % value) == domain or ('https://%s' % value) == domain:
                        del domains[key]
                item['domains'] = domains
                self.db.domain.save(item)

            for informer in self.db.informer.find({'domain': domain}):
                informer_id = informer['guid']
                self.db.informer.remove({'guid': informer_id}, multi=True)
                mq.MQ().informer_stop(informer_id)

            self.db.domain.categories.remove({'domain': domain}, multi=True)
            mq.MQ().domain_stop(domain)

            self.db.user.domains.update({'login': self.account.login},
                                        {'$pull': {'domain': domain}}, upsert=True)
            mq.MQ().account_update(self.account.login)

    def get_login(self):
        return self._login

    def set_login(self, val):
        self._login = val.rstrip()

    login = property(get_login, set_login)

    def get_account_type(self):
        if not self.loaded: self.load()
        return self._account_type

    def set_account_type(self, val):
        self._account_type = val

    account_type = property(get_account_type, set_account_type)

    User = 'user'
    Manager = 'manager'
    Administrator = 'administrator'

    def __init__(self, login):
        self.login = login
        self.guid = str(uuid1())
        self.guid_int = uuid_to_long(self.guid)
        self.email = ''
        self.skype = ''
        self.password = ''
        self.phone = ''
        self.owner_name = ''
        self.min_out_sum = 100
        self.click_percent = 50
        self.click_cost_min = 0.01
        self.click_cost_max = 1.00
        self.imp_percent = 50
        self.imp_cost_min = 0.05
        self.imp_cost_max = 2.00
        self.range_short_term = (100 / 100.0)
        self.range_long_term = (0 / 100.0)
        self.range_context = (0 / 100.0)
        self.range_search = (100 / 100.0)
        self.range_retargeting = (100 / 100.0)
        self.manager_get = None
        self.registration_date = datetime.datetime.now()
        self.account_type = Account.User
        self.db = app_globals.db
        self.db_m = app_globals.db_m
        self.report = AccountReports(self)
        self.domains = Account.Domains(self)
        self.loaded = False
        self.money_out_paymentType = []
        self.money_web_z = False
        self.money_web_r = False
        self.money_web_u = False
        self.money_cash = False
        self.money_card = False
        self.money_card_pb_ua = False
        self.money_card_pb_us = False
        self.money_factura = False
        self.money_yandex = False
        self.prepayment = False

        #: Заблокирован ли аккаунт
        #: Может принимать значения:
        #:     False или '': не заблокирован
        #:     'light': временная приостановка, которую может снять сам пользователь
        #:     'banned': аккаунт заблокирован полностью (за нарушение) 
        self.blocked = False
        self.time_filter_click = 15
        self.cost_percent_click = 100

    def register(self):
        ''' Регистрирует пользователя '''
        try:
            assert self.login, 'Login must be specified'
            assert self.db, 'Database connection must be assigned'
            if self.money_web_z:
                self.money_out_paymentType.append(u'webmoney_z')
            if self.money_web_r:
                self.money_out_paymentType.append(u'webmoney_r')
            if self.money_web_u:
                self.money_out_paymentType.append(u'webmoney_u')
            if self.money_cash:
                self.money_out_paymentType.append(u'cash')
            if self.money_card:
                self.money_out_paymentType.append(u'card')
            if self.money_card_pb_ua:
                self.money_out_paymentType.append(u'card_pb_ua')
            if self.money_card_pb_us:
                self.money_out_paymentType.append(u'card_pb_us')
            if self.money_factura:
                self.money_out_paymentType.append(u'factura')
            if self.money_yandex:
                self.money_out_paymentType.append(u'yandex')
            cost = {'ALL': {'click': {'percent': int(self.click_percent), 'cost_min': float(self.click_cost_min),
                                      'cost_max': float(self.click_cost_max)}, \
                            'imp': {'percent': int(self.imp_percent), 'cost_min': float(self.imp_cost_min),
                                    'cost_max': float(self.imp_cost_max)}}}
            self.db.users.insert({'login': self.login,
                                  'guid': self.guid,
                                  'guid_int': self.guid_int,
                                  'password': self.password,
                                  'registrationDate': self.registration_date,
                                  'email': self.email,
                                  'skype': self.skype,
                                  'phone': self.phone,
                                  'ownerName': self.owner_name,
                                  'cost': cost,
                                  'minOutSum': self.min_out_sum,
                                  'managerGet': self.manager_get,
                                  'manager': self._account_type in (Account.Manager),
                                  'accountType': self._account_type,
                                  'moneyOutPaymentType': self.money_out_paymentType,
                                  'blocked': False,
                                  'range_short_term': float(self.range_short_term),
                                  'range_long_term': float(self.range_long_term),
                                  'range_context': float(self.range_context),
                                  'range_search': float(self.range_search),
                                  'range_retargeting': float(self.range_retargeting),
                                  })
            self.loaded = True
            mq.MQ().account_update(self.login)
        except (pymongo.errors.DuplicateKeyError, pymongo.errors.OperationFailure) as e:
            print(e)
            raise Account.AlreadyExistsError(self.login)

    def update(self):
        ''' Обновляет данные пользователя'''
        try:
            self.money_out_paymentType = []
            if self.money_web_z:
                self.money_out_paymentType.append(u'webmoney_z')
            if self.money_web_r:
                self.money_out_paymentType.append(u'webmoney_r')
            if self.money_web_u:
                self.money_out_paymentType.append(u'webmoney_u')
            if self.money_cash:
                self.money_out_paymentType.append(u'cash')
            if self.money_card:
                self.money_out_paymentType.append(u'card')
            if self.money_card_pb_ua:
                self.money_out_paymentType.append(u'card_pb_ua')
            if self.money_card_pb_us:
                self.money_out_paymentType.append(u'card_pb_us')
            if self.money_factura:
                self.money_out_paymentType.append(u'factura')
            if self.money_yandex:
                self.money_out_paymentType.append(u'yandex')
            self.db.users.update({'login': self.login},
                                 {'$set': {
                                     'password': self.password,
                                     'registrationDate': self.registration_date,
                                     'email': self.email,
                                     'skype': self.skype,
                                     'phone': self.phone,
                                     'ownerName': self.owner_name,
                                     'cost.ALL.click.percent': int(self.click_percent),
                                     'cost.ALL.click.cost_min': float(self.click_cost_min),
                                     'cost.ALL.click.cost_max': float(self.click_cost_max),
                                     'cost.ALL.imp.percent': int(self.imp_percent),
                                     'cost.ALL.imp.cost_min': float(self.imp_cost_min),
                                     'cost.ALL.imp.cost_max': float(self.imp_cost_max),
                                     'minOutSum': self.min_out_sum,
                                     'managerGet': self.manager_get,
                                     'manager': self._account_type in (Account.Manager),
                                     'accountType': self._account_type,
                                     'moneyOutPaymentType': self.money_out_paymentType,
                                     'prepayment': self.prepayment,
                                     'blocked': self.blocked,
                                     'time_filter_click': self.time_filter_click,
                                     'cost_percent_click': self.cost_percent_click,
                                     'range_short_term': float(self.range_short_term),
                                     'range_long_term': float(self.range_long_term),
                                     'range_context': float(self.range_context),
                                     'range_search': float(self.range_search),
                                     'range_retargeting': float(self.range_retargeting),
                                 }})

            # При блокировании менеджера, снимаем ответственного менеджера с сайта
            if self._account_type == Account.Manager and self.blocked == 'banned':
                self.db.users.update({'managerGet': self.login},
                                     {'$set': {'managerGet': ''}},
                                     multi=True)

            mq.MQ().account_update(self.login)
        except Exception as e:
            print e
            raise Account.UpdateError(self.login)

    def load(self):
        ''' Загружает аккаунт '''
        assert self.login, 'Login must be specified'

        record = self.db.users.find_one({'login': self.login})
        if not record:
            raise Account.NotFoundError(self.login)
        self.guid = record['guid']
        self.guid_int = record.get('guid_int', uuid_to_long(self.guid))
        self.password = record['password']
        self.registration_date = record['registrationDate']
        self.email = record.get('email', '')
        self.skype = record.get('skype', '')
        self.phone = record.get('phone', '')
        self.owner_name = record.get('ownerName', '')
        self.prepayment = record.get('prepayment', False)
        self.click_percent = int(record.get('cost', {}).get('ALL', {}).get('click', {}).get('percent', 50))
        self.click_cost_min = float(record.get('cost', {}).get('ALL', {}).get('click', {}).get('cost_min', 0.01))
        self.click_cost_max = float(record.get('cost', {}).get('ALL', {}).get('click', {}).get('cost_max', 1.00))
        self.imp_percent = int(record.get('cost', {}).get('ALL', {}).get('imp', {}).get('percent', 50))
        self.imp_cost_min = float(record.get('cost', {}).get('ALL', {}).get('imp', {}).get('cost_min', 0.05))
        self.imp_cost_max = float(record.get('cost', {}).get('ALL', {}).get('imp', {}).get('cost_max', 2.00))
        self.range_short_term = float(record.get('range_short_term', (100 / 100.0)))
        self.range_long_term = float(record.get('range_long_term', (0 / 100.0)))
        self.range_context = float(record.get('range_context', (0 / 100.0)))
        self.range_search = float(record.get('range_search', (100 / 100.0)))
        self.range_retargeting = float(record.get('range_retargeting', (100 / 100.0)))
        try:
            self.min_out_sum = float(record.get('minOutSum', 100))
        except:
            self.min_out_sum = 100
        self.manager_get = record.get('managerGet')
        self.money_out_paymentType = record.get('moneyOutPaymentType') or ['webmoney_z']
        self.money_web_z = 'webmoney_z' in self.money_out_paymentType
        self.money_web_r = 'webmoney_r' in self.money_out_paymentType
        self.money_web_u = 'webmoney_u' in self.money_out_paymentType
        self.money_cash = 'cash' in self.money_out_paymentType
        self.money_card = 'card' in self.money_out_paymentType
        self.money_card_pb_ua = 'card_pb_ua' in self.money_out_paymentType
        self.money_card_pb_us = 'card_pb_us' in self.money_out_paymentType
        self.money_factura = 'factura' in self.money_out_paymentType
        self.money_yandex = 'yandex' in self.money_out_paymentType
        self.blocked = record.get('blocked', False)
        self.time_filter_click = record.get('time_filter_click', 15)
        self.cost_percent_click = record.get('cost_percent_click', 100)
        acc_type = record.get('accountType', 'user')
        if acc_type == 'manager':
            self.account_type = Account.Manager
        elif acc_type == 'administrator':
            self.account_type = Account.Administrator
        else:
            self.account_type = Account.User
        self.loaded = True

    def informers(self, ):
        """ Возвращает список информеров данного пользователя """
        result = []
        for object in self.db.informer.find({'user': self.login}):
            informer = Informer.load_from_mongo_record(object)
            result.append(informer)
        return result

    def getManagerInfo(self):
        r = self.db.users.find_one({'login': self.manager_get})
        return {'name': r.get('ownerName', ''), 'email': r.get('email', ''), 'skype': r.get('skype', '')}

    def exists(self):
        """ Возвращает True, если пользователь с данным login существует, иначе False """
        return True if self.db.users.find_one({'login': self.login}) else False

    @staticmethod
    def active_managers():
        ''' Возвращает список активных менеджеров '''
        return [x['login']
                for x in app_globals.db.users.find({
                'manager': True,
                "accountType": "manager",
                'blocked': {'$ne': 'banned'}})]

    @staticmethod
    def makePassword():
        """Возвращает сгенерированный пароль"""
        from random import Random
        rng = Random()

        righthand = '23456qwertasdfgzxcvbQWERTASDFGZXCVB'
        lefthand = '789yuiophjknmYUIPHJKLNM'
        allchars = righthand + lefthand

        passwordLength = 8
        alternate_hands = True
        password = ''

        for i in range(passwordLength):
            if not alternate_hands:
                password += rng.choice(allchars)
            else:
                if i % 2:
                    password += rng.choice(lefthand)
                else:
                    password += rng.choice(righthand)
        return password


class AccountReports():
    """ Отчёты по аккаунту пользователя """

    def __init__(self, account):
        if isinstance(account, Account):
            self.account = account
        else:
            raise ValueError(), "account should be an Account instance or login string!"
        self.db = app_globals.db
        self.db_m = app_globals.db_m

    def balance(self):
        """Возвращает сумму на счету пользователя """
        # Доход
        try:
            pipeline = [{'$match': {'user': self.account.login}},
                        {'$group': {
                            '_id': 'null',
                            'sum': {'$sum': '$totalCost'}}
                        }
                        ]
            cursor = self.db_m.stats.daily.user.aggregate(pipeline=pipeline)
            try:
                income = cursor.next()
            except StopIteration:
                income = {}
            income = float(income.get('sum', 0))
        except Exception as e:
            print e
            income = 0.0

        # Сумма выведенных денег
        try:
            money_out = sum([x.get('summ', 0) for x in self.money_out_requests(approved=True)])
            money_out = float(money_out)
        except:
            money_out = 0.0

        return income - money_out

    def outBalance(self):
        """Возвращает сумму на счету пользователя """
        # Доход
        try:
            pipeline = [{'$match': {'user': self.account.login}},
                        {'$group': {
                            '_id': 'null',
                            'sum': {'$sum': '$totalCost'}}
                        }
                        ]
            cursor = self.db_m.stats.daily.user.aggregate(pipeline=pipeline)
            try:
                income = cursor.next()
            except StopIteration:
                income = {}
            income = float(income.get('sum', 0))
        except Exception as e:
            print e
            income = 0.0

        # Сумма выведенных денег
        try:
            money_out = sum([x.get('summ', 0) for x in self.money_out_requests()])
            money_out = float(money_out)
        except:
            money_out = 0.0

        return income - money_out

    def money_out_requests(self, approved=None):
        """ Возращает список заявок на вывод средств.
            Если approved == None, то вернёт все заявки.
            Если approved == True, то вернёт только подтверждённые заявки
            Если approved == False, то вернёт только неподтверждённые заявки
        """
        condition = {'user.login': self.account.login}
        if isinstance(approved, bool):
            if approved:
                condition['approved'] = approved
            else:
                condition['$or'] = [{"approved": {"$exists": approved}}, {"approved": approved}]
        data = self.db_m.money_out_request.find(condition)
        return list(data)


class ManagerReports():
    """ Отчёты по менеджеру """

    def __init__(self, account):
        if isinstance(account, Account):
            self.account = account
        else:
            raise ValueError(), "account should be an Account instance or login string!"
        assert account.account_type == Account.Manager, "account_type must be Account.Manager"
        self.db = app_globals.db

    def money_out_requests(self, approved=None):
        """ Возращает список заявок на вывод средств.
            Если approved == None, то вернёт все заявки.
            Если approved == True, то вернёт только подтверждённые заявки
            Если approved == False, то вернёт только неподтверждённые заявки
        """
        condition = {'user.login': self.account.login}
        if isinstance(approved, bool):
            condition['approved'] = {'$ne': (not approved)}
        data = self.db.money_out_request.find(condition)
        return list(data)

    def monthProfitPerDate(self, dateStart=None):
        ''' Каждодневный доход за последние 30 дней'''
        totalCost = 0
        manager = self.account.login
        if dateStart is None:
            dateStart = datetime.datetime.today() - datetime.timedelta(days=30)
        dateEnd = datetime.datetime.today()
        dateStart = datetime.datetime(dateStart.year, dateStart.month, dateStart.day, 0, 0)
        dateEnd = datetime.datetime(dateEnd.year, dateEnd.month, dateEnd.day, 0, 0)
        data = []
        sum = 0
        for x in self.db.stats_manager_overall_by_date.find(
                {'login': manager, "date": {"$gte": dateStart, "$lt": dateEnd}}).sort("date", pymongo.DESCENDING):
            persent = float(x['totalCost'] / (x['adload_cost'] / 100.0)) if (
                x['totalCost'] > 0 and x['adload_cost'] > 0) else 0.0
            data.append((x['date'].strftime('%Y.%m.%d'),
                         manager,
                         formatMoney(x['totalCost']),
                         '%.3f %%' % persent,
                         formatMoney(x['income']),
                         formatMoney(x['adload_cost']),
                         x['activ_users'],
                         x['all_users']))

        userdata = {}

        return [data, userdata]

    def monthBalance(self):
        ''' Возвращает заработок за последние 30 дней'''
        sum = 0
        manager = self.account.login
        dateStart = datetime.datetime.today() - datetime.timedelta(days=30)
        dateEnd = datetime.datetime.today()
        dateStart = datetime.datetime(dateStart.year, dateStart.month, dateStart.day, 0, 0)
        dateEnd = datetime.datetime(dateEnd.year, dateEnd.month, dateEnd.day, 0, 0)
        for x in self.db.stats_manager_overall_by_date.find(
                {'login': manager, "date": {"$gte": dateStart, "$lt": dateEnd}}):
            sum += x['managerInvoce']
        return float(sum)

    def balance(self):
        """ Возвращает сумму на счету менеджера """
        totalCost = 0
        manager = self.account.login
        income = 0
        for x in self.db.stats_manager_overall_by_date.find({'login': manager}):
            income += x['managerInvoce']

        # Сумма выведенных денег
        try:
            money_out = sum([x.get('summ', 0) for x in self.money_out_requests(approved=True)])
            money_out = float(money_out)
        except:
            money_out = 0.0

        return income - money_out


class Permission():
    """ Права пользователей """

    VIEW_ALL_USERS_STATS = 'view all users stats'  # Может просматривать статистику всех пользователей, а не только тех, кого привёл
    VIEW_MONEY_OUT = 'view money out'  # Может просматривать историю вывода денежных средств
    USER_DOMAINS_MODERATION = 'user domains moderation'  # Может одобрять/отклонять заявки на регистрацию
    SET_CLICK_COST = 'set click cost'  # Может устанаваливать цену за клик для пользователя
    REGISTER_USERS_ACCOUNT = 'register users account'  # Может регистрировать пользовательские аккаунты
    EDIT_USERS_ACCOUNT = 'register users account'  # Может регистрировать пользовательские аккаунты
    MANAGE_USER_INFORMERS = 'manage user informers'  # Может настраивать информеры пользователей (в т.ч. и расширенные настройки)

    class InsufficientRightsError(Exception):
        """ Недостаточно прав для выполнения операции """
        pass

    def __init__(self, account):
        assert account and isinstance(account, Account), "'account' must be an Account instance"
        if not account.exists():
            raise Account.NotFoundError(account)
        self.account = account
        self.permissions = set()

    def has(self, right=None):
        ''' Возвращает ``True``, если пользователь имеет данное разрешение, иначе ``False`` '''
        if self.account.account_type == Account.Administrator:
            return True
        if self.account.account_type == Account.Manager:
            if right == self.EDIT_USERS_ACCOUNT:
                return True
            if right == self.SET_CLICK_COST:
                return True
            if right == self.REGISTER_USERS_ACCOUNT:
                return True
        if right in self.permissions:
            return True
        return False