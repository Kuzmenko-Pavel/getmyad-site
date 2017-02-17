# -*- coding: utf-8 -*-

import re
import os
import sys
import smtplib
import mimetypes

import email.Charset
from email import encoders
from email.header import Header
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart

from mako import exceptions
from mako.template import Template
from mako.lookup import TemplateLookup

TEMPLATES_DIRS = [os.getcwdu()]
TEMPLATES_CACHE_DIR = os.getcwdu()
COMMASPACE_SEPARATOR = ', '

#TODO сделать свой класс исключений
#email.Charset.add_charset('utf-8', email.Charset.SHORTEST, None, None)

class Letter(object):

    _subject = None
    _sender = None
    _sender_name = None
    _recipients = None
    _template = None
    _message_props = None
    _outer = None
    _attachments = None

    @property
    def subject(self):
        if self._subject:
            return self._subject
        raise Exception('Please set subject attribute.')

    @subject.setter
    def subject(self, subject):
        self._subject = subject

    @property
    def sender(self):
        if self._sender:
            return self._sender
        raise Exception('Please set sender attribute.')

    @sender.setter
    def sender(self, sender):
        if self._email_is_valid(sender):
            self._sender = sender
        else:
            raise Exception('Invalid email %s' % sender)

    @property
    def sender_name(self):
        if self._sender_name:
            return self._sender_name
        raise Exception('Please set sender_name attribute.')

    @sender_name.setter
    def sender_name(self, sender_name):
        self._sender_name = sender_name

    @property
    def recipients(self):
        if self._recipients:
            return self._recipients.split(COMMASPACE_SEPARATOR)
        raise Exception('Please set recipients attribute.')

    @recipients.setter
    def recipients(self, recipients):
        if not isinstance(recipients, list):
            if self._email_is_valid(recipients):
                self._recipients = recipients
            else:
                raise Exception('Invalid email %s' % recipients)
        else:
            for recipient in recipients:
                if not self._email_is_valid(recipient):
                    raise Exception('Invalid email %s' % recipient)
            self._recipients = COMMASPACE_SEPARATOR.join(recipients)

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, template_file):
        templates_lookup = TemplateLookup(directories=TEMPLATES_DIRS, input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace', default_filters=['decode.utf8'])
        self._template = templates_lookup.get_template(template_file)
        if self._message_props:
            self.set_message(self._message_props)


    def __init__(self):
        pass


    def send(self, server, port, login='', password=''):
        self._outer['Subject'] = self.subject
        self._outer['To'] = COMMASPACE_SEPARATOR.join(self.recipients)

        if self._sender_name:
            sender_name = Header(self.sender_name, 'utf-8')
            self._outer['From'] = str(sender_name) + ' <' + self.sender + '>'
        else:
            self._outer['From'] = self.sender

        s = smtplib.SMTP(server, port)
        s.ehlo()
        s.login(login, password)
        s.sendmail(self.sender, self.recipients, self._outer.as_string())


    def set_message(self, *args, **kwargs):
        if 'type' not in kwargs:
            kwargs['type'] = 'plain'

        if len(args):
            kwargs['message'] = args[0]

        if not self._message_props:
            self._message_props = kwargs

        if self.template:
            msg = MIMEText(self.template.render(**kwargs), kwargs['type'], _charset='utf-8')
        else:
            msg = MIMEText(kwargs['message'], kwargs['type'], _charset='utf-8')

        if self._outer:
            if isinstance(self._outer, MIMEMultipart):
                self._outer.attach(msg)
        else:
            self._outer = msg
            

    def attach(self, file_name):
        """
        if not self._outer:
        """
        raise NotImplementedError('attach not implemented')


    def _email_is_valid(self, address):
        qtext = '[^\\x0d\\x22\\x5c\\x80-\\xff]'
        dtext = '[^\\x0d\\x5b-\\x5d\\x80-\\xff]'
        atom = '[^\\x00-\\x20\\x22\\x28\\x29\\x2c\\x2e\\x3a-\\x3c\\x3e\\x40\\x5b-\\x5d\\x7f-\\xff]+'
        quoted_pair = '\\x5c[\\x00-\\x7f]'
        domain_literal = "\\x5b(?:%s|%s)*\\x5d" % (dtext, quoted_pair)
        quoted_string = "\\x22(?:%s|%s)*\\x22" % (qtext, quoted_pair)
        domain_ref = atom
        sub_domain = "(?:%s|%s)" % (domain_ref, domain_literal)
        word = "(?:%s|%s)" % (atom, quoted_string)
        domain = "%s(?:\\x2e%s)*" % (sub_domain, sub_domain)
        local_part = "%s(?:\\x2e%s)*" % (word, word)
        addr_spec = "%s\\x40%s" % (local_part, domain)

        email_address = re.compile('\A%s\Z' % addr_spec)

        return email_address.match(address)


if __name__ == "__main__":
    letter = Letter()
    letter.subject = 'testing message'
    letter.sender = 'support@yottos.com'
    letter.recipients = ['sgorlumel@gmail.com']
    letter.template = 'sometemplate.mako.html'
    letter.set_message(content=u'проверка связи2', type='html')
    letter.send()
