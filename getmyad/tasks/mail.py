# -*- coding: utf-8 -*-
import letter
from letter import Letter
from celery.task import task
import os

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
