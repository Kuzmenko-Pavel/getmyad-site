# This Python file uses the following encoding: utf-8
from getmyad.model.Account import AccountReports, Account, ManagerReports
import getmyad.tasks.mail as mail
from pylons import app_globals
import datetime
import uuid


class MoneyOutRequest(object):
    """Запрос на вывод средств"""
    
    class NotEnoughMoney(Exception):
        """ Недостаточно денег для формирования заявки """
        pass
    
    class NotConfirm(Exception):
        """ Недостаточно денег для формирования заявки """
        pass
    
    def __init__(self):
        self.date = datetime.datetime.now()
        self.account = None
        self.summ = 0
        self.comment = ''
        self.confirm_guid = uuid.uuid4().hex
        self.ip = ''
    
    def save(self):
        """ Сохранение заявки """
        if not self._check_money_out_possibility():
            raise MoneyOutRequest.NotEnoughMoney()
        if not self._check_money_out_not_confirm():
            raise MoneyOutRequest.NotConfirm()
            
        req = {'date': self.date,
               'summ': int(self.summ),
               'confirm_guid': self.confirm_guid,
               'user': {'login': self.account.login},
               'comment': self.comment,
               'ip': self.ip
               }
        payment_details = self._get_payment_details()
        assert isinstance(payment_details, dict)
        req.update(payment_details)
        app_globals.db.money_out_request.save(req)
        print "Saving: %s" % req
    
    def _get_payment_details(self):
        """ Возвращает словарь со свойствами, специфичными для каждого метода оплаты """
        return {}
    
    def _get_payment_details_for_email(self):
        """ Текстовое описание подробностей метода вывода для отправки по e-mail """
        return ''

    def _check_money_out_not_confirm(self):
        """ Возвращает true, если заявку с заданными параметрами возможно
            создать (у клиента должно быть достаточно денег на счету и т.д.) """
        
        if not self.account.loaded:
            self.account.load()
        not_confirm = AccountReports(self.account).money_out_requests(approved=False)
        if len(not_confirm) > 0:
            return False
        return True

    def _check_money_out_possibility(self):
        """ Возвращает true, если заявку с заданными параметрами возможно
            создать (у клиента должно быть достаточно денег на счету и т.д.) """
        if not self.account.loaded:
            self.account.load()
        if not self.account.prepayment:
            if self.account.account_type == Account.User:
                balance = AccountReports(self.account).balance()
            elif self.account.account_type == Account.Manager:
                balance = ManagerReports(self.account).balance()
            else:
                return False
            
            if self.summ > balance:
                return False
        return True
    
    def _validate_fields(self):
        """ Проверка полей на корректность """
        # TODO: Not implemented! 
        pass

    def send_confirmation_email(self):
        """ Отправка письма на e-mail пользователя с требованием подтвердить вывод средств """
        if not self.account.loaded:
            self.account.load()

        email = self.account.email
        payment_details = self._get_payment_details_for_email()
        confirm_link = "http://getmyad.yottos.com/private/confirmRequestToApproveMoneyOut/%s" % self.confirm_guid
        date_expire = (datetime.datetime.today() + datetime.timedelta(days=3)).strftime('%d.%m.%y %H:%M')
        try:
            mail.confirmation_email.delay(email=email, payment_details=payment_details, confirm_link=confirm_link, date_expire=date_expire)
        except Exception as ex:
            mail.confirmation_email(email=email, payment_details=payment_details, confirm_link=confirm_link, date_expire=date_expire)


    def load(self, confirm_guid):
        """ Загружает заявку с кодом подтверждения confirm_guid """
        x = app_globals.db.money_out_request.find_one({'confirm_guid': confirm_guid})
        self.date = x['date']
        self.account = Account(x['user']['login'])
        self.comment = x['comment']
        self.confirm_guid = x['confirm_guid']
        self.summ = x['summ'] 


class WebmoneyMoneyOutRequest(MoneyOutRequest):
    """ Запрос на вывод средств посредством WebMoney """
    
    def __init__(self):
        MoneyOutRequest.__init__(self)
        self.webmoney_login = ''
        self.webmoney_account_number = ''
        self.phone = ''
    
    def _get_payment_details(self):
        return {'paymentType': 'webmoney_z',
                'webmoneyLogin': self.webmoney_login,
                'webmoneyAccount': self.webmoney_account_number,
                'phone': self.phone
                }

    def _get_payment_details_for_email(self):
        return u'''
Сумма: %s грн
Тип вывода средств: webmoney-z'
WMID: %s
Номер кошелька: %s 
 ''' % (self.summ, 
        self.webmoney_login,
        self.webmoney_account_number)


class WebmoneyMoneyOutRequest_r(MoneyOutRequest):
    """ Запрос на вывод средств посредством WebMoney """
    
    def __init__(self):
        MoneyOutRequest.__init__(self)
        self.webmoney_login = ''
        self.webmoney_account_number = ''
        self.phone = ''
    
    def _get_payment_details(self):
        return {'paymentType': 'webmoney_r',
                'webmoneyLogin': self.webmoney_login,
                'webmoneyAccount': self.webmoney_account_number,
                'phone': self.phone
                }

    def _get_payment_details_for_email(self):
        return u'''
Сумма: %s грн
Тип вывода средств: webmoney-r'
WMID: %s
Номер кошелька: %s 
 ''' % (self.summ, 
        self.webmoney_login,
        self.webmoney_account_number)


class WebmoneyMoneyOutRequest_u(MoneyOutRequest):
    """ Запрос на вывод средств посредством WebMoney """
    
    def __init__(self):
        MoneyOutRequest.__init__(self)
        self.webmoney_login = ''
        self.webmoney_account_number = ''
        self.phone = ''
    
    def _get_payment_details(self):
        return {'paymentType': 'webmoney_u',
                'webmoneyLogin': self.webmoney_login,
                'webmoneyAccount': self.webmoney_account_number,
                'phone': self.phone
                }

    def _get_payment_details_for_email(self):
        return u'''
Сумма: %s грн
Тип вывода средств: webmoney-u'
WMID: %s
Номер кошелька: %s 
 ''' % (self.summ, 
        self.webmoney_login,
        self.webmoney_account_number)


class CardMoneyOutRequest(MoneyOutRequest):
    """ запрос на вывод средств посредством банковской карты """
    
    def __init__(self):
        MoneyOutRequest.__init__(self)
        self.card_number = ''
        self.card_name = ''
        self.card_type = ''
        self.card_phone = ''
        self.expire_year = ''
        self.expire_month = ''
        self.bank = ''
        self.bank_mfo = ''
        self.bank_okpo = ''
        self.bank_transit_account = ''
        self.card_currency = ''
        
    def _get_payment_details(self):
        return { 'paymentType': 'card',
                 'cardNumber': self.card_number,
                 'cardName': self.card_name,
                 'cardType': self.card_type,
                 'phone': self.card_phone,
                 'expire_year': self.expire_year,
                 'expire_month': self.expire_month,
                 'bank': self.bank,
                 'bank_MFO': self.bank_mfo,
                 'bank_OKPO': self.bank_okpo,
                 'bank_TransitAccount': self.bank_transit_account,
                 'cardCurrency': self.card_currency
               }
    
    def _get_payment_details_for_email(self):
        return u'''
тип вывода средств: банковская карта %(cardType)s
владелец: %(cardName)s
банк: %(bank)s
мфо банка: %(bank_MFO)s
окпо банка: %(bank_OKPO)s
транзитный счёт банка: %(bank_TransitAccount)s
номер карты: %(cardNumber)s
срок действия карты: %(expire_month)s / %(expire_year)s
''' % self._get_payment_details() + \
u'''сумма: %s грн
''' % self.summ


class InvoiceMoneyOutRequest(MoneyOutRequest):
    """ Запрос на вывод средств посредством счёт-фактуры """
    
    def __init__(self):
        MoneyOutRequest.__init__(self)
        self.contacts = ''
        self.phone = ''
        self.invoice_filename = ''
    
    def _get_payment_details(self):
        return { 'paymentType': 'factura',
                 'contact': self.contacts,
                 'phone': self.phone,
                 'schet_factura_file_name': self.invoice_filename
               }
    
    def _get_payment_details_for_email(self):
        return u'''
Вывод средств посредством счёт-фактуры.
'''


class YandexMoneyOutRequest(MoneyOutRequest):
    """ Запрос на вывод средств посредством Яндекс.Деньги """
    def __init__(self):
        MoneyOutRequest.__init__(self)
        self.yandex_number = ''
        self.phone = ''
        
    def _get_payment_details(self):
        return {'paymentType': 'yandex',
                'yandex_number': self.yandex_number,
                'phone': self.phone
                }

    def _get_payment_details_for_email(self):
        return u'''Сумма: %s грн
                   Тип вывода средств: Яндекс.Деньги'
                   Номер счета: %s''' % (self.summ,  self.yandex_number)


class CashMoneyOutRequest(MoneyOutRequest):
    """ запрос на вывод средств наличными"""
    
    def __init__(self):
        MoneyOutRequest.__init__(self)
        self.phone = ''
        
    def _get_payment_details(self):
        return { 'paymentType': 'cash',
                 'phone': self.phone,
               }
    
    def _get_payment_details_for_email(self):
        return u'''
тип вывода средств: наличными
сумма: %s грн
''' % self.summ


class CardMoneyOutRequest_pb_ua(MoneyOutRequest):
    """ запрос на вывод средств посредством банковской карты """
    
    def __init__(self):
        MoneyOutRequest.__init__(self)
        self.card_number = ''
        self.card_name = ''
        self.card_type = ''
        self.card_phone = ''
        self.expire_year = ''
        self.expire_month = ''
        self.card_currency = 'UAH'
        
    def _get_payment_details(self):
        return { 'paymentType': 'card_pb_ua',
                 'cardNumber': self.card_number,
                 'cardName': self.card_name,
                 'cardType': self.card_type,
                 'phone': self.card_phone,
                 'expire_year': self.expire_year,
                 'expire_month': self.expire_month,
                 'cardCurrency': self.card_currency
               }
    
    def _get_payment_details_for_email(self):
        return u'''
тип вывода средств: банковская карта %(cardType)s
владелец: %(cardName)s
банк: ПриватБанк
номер карты: %(cardNumber)s
срок действия карты: %(expire_month)s / %(expire_year)s
''' % self._get_payment_details() + u'''сумма: %s грн''' % self.summ


class CardMoneyOutRequest_pb_us(MoneyOutRequest):
    """ запрос на вывод средств посредством банковской карты """
    
    def __init__(self):
        MoneyOutRequest.__init__(self)
        self.card_number = ''
        self.card_name = ''
        self.card_type = ''
        self.card_phone = ''
        self.expire_year = ''
        self.expire_month = ''
        self.card_currency = 'USD'
        
    def _get_payment_details(self):
        return { 'paymentType': 'card_pb_us',
                 'cardNumber': self.card_number,
                 'cardName': self.card_name,
                 'cardType': self.card_type,
                 'phone': self.card_phone,
                 'expire_year': self.expire_year,
                 'expire_month': self.expire_month,
                 'cardCurrency': self.card_currency
               }
    
    def _get_payment_details_for_email(self):
        return u'''
тип вывода средств: банковская карта %(cardType)s
владелец: %(cardName)s
банк: ПриватБанк
номер карты: %(cardNumber)s
срок действия карты: %(expire_month)s / %(expire_year)s
''' % self._get_payment_details() + u'''сумма: %s грн''' % self.summ
