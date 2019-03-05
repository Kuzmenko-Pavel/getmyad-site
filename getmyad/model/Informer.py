# -*- coding: UTF-8 -*-
from ftplib import FTP
from uuid import uuid4
import StringIO
import datetime
import logging
import json

from getmyad.lib.helpers import progressBar, uuid_to_long, to_int
from getmyad.model.mq import MQ
from pylons import config, app_globals
import re
from slimit import minifier


class Informer:
    """ Рекламный информер (он же рекламный скрипт, рекламная выгрузка) """

    def __init__(self):
        """

        """
        self.guid = None
        self.guid_int = None
        self.dynamic = False
        self.title = None
        self.admaker = None
        self.user_login = None
        self.user_guid = None
        self.user_guid_int = None
        self.non_relevant = None
        self.domain = None
        self.domain_guid = None
        self.domain_guid_int = None
        self.height = None
        self.width = None
        self.height_banner = None
        self.width_banner = None
        self.cost = None
        self.range_short_term = None
        self.range_long_term = None
        self.range_context = None
        self.range_search = None
        self.range_retargeting = None
        self.html_notification = False
        self.plase_branch = True
        self.retargeting_branch = True
        self.auto_reload = 0
        self.blinking_reload = False
        self.shake_reload = False
        self.shake_mouse = False
        self.blinking = 0
        self.shake = 0
        self.rating_division = 1000
        self.rating_hard_limit = False
        self.disable_filter = False
        self.db = app_globals.db

    def user_by_login(self, login):
        record = self.db.users.find_one({'login': login})
        return record

    def save(self):
        """ Сохраняет информер, при необходимости создаёт """
        update = {}
        if not self.guid:
            self.guid = str(uuid4()).lower()
            if not self.user_login:
                raise ValueError('User login must be specified when creating '
                                 'informer!')
            update['user'] = self.user_login

        if not self.guid_int:
            self.guid_int = uuid_to_long(self.guid)
            update['guid_int'] = self.guid_int

        if self.user_login is not None:
            record = self.user_by_login(self.user_login)
            if not self.user_guid:
                self.user_guid = record.get('guid')
            if not self.user_guid_int:
                self.user_guid_int = record.get('guid_int', uuid_to_long(self.user_guid))
            update['range_short_term'] = self.range_short_term = float(record.get('range_short_term', 1))
            update['range_long_term'] = self.range_long_term = float(record.get('range_long_term', 0))
            update['range_context'] = self.range_context = float(record.get('range_context', 0))
            update['range_search'] = self.range_search = float(record.get('range_search', 1))
            update['retargeting_capacity'] = self.range_retargeting = float(record.get('range_retargeting', 1))
        else:
            self.range_short_term = 1.0
            self.range_long_term = 0.0
            self.range_context = 0.0
            self.range_search = 1.0
            self.range_retargeting = 1.0
            update['user'] = self.user_login
            update['range_short_term'] = self.range_short_term
            update['range_long_term'] = self.range_long_term
            update['range_context'] = self.range_context
            update['range_search'] = self.range_search
            update['retargeting_capacity'] = self.range_retargeting

        domain_exists = False
        record = self.db.domain.find_one({'login': self.user_login})
        if record:
            obj = record.get('domains', {})
            for k, v in obj.iteritems():
                if v == self.domain:
                    domain_exists = True
                    break
        if not domain_exists:
            raise ValueError('Domain not set!')

        update['dynamic'] = self.dynamic
        if self.title:
            update['title'] = self.title
        if self.admaker:
            update['admaker'] = self.admaker
        if not self.domain:
            record = self.db.domain.find_one({'login': self.user_login})
            if record:
                obj = record.get('domains', {})
                if obj.values():
                    self.domain = obj.values()[0]
                else:
                    raise ValueError('Domain not set!')
            else:
                raise ValueError('Domain not set!')
        if self.domain:
            update['domain'] = self.domain
            record = self.db.domain.find_one({'login': self.user_login})
            if record:
                if not self.domain_guid:
                    obj = record.get('domains', {})
                    for k, v in obj.iteritems():
                        if v == self.domain:
                            self.domain_guid = k
                            break
                if not self.domain_guid_int:
                    obj = record.get('domains_int', {})
                    for k, v in obj.iteritems():
                        if v == self.domain:
                            self.domain_guid_int = k
                            break
                    else:
                        self.domain_guid_int = uuid_to_long(self.domain_guid)
            else:
                raise ValueError('Domain not set!')

        if self.user_guid:
            update['user_guid'] = self.user_guid

        if self.user_guid_int:
            update['user_guid_int'] = self.user_guid_int

        if self.domain_guid:
            update['domain_guid'] = self.domain_guid

        if self.domain_guid_int:
            update['domain_guid_int'] = self.domain_guid_int

        if self.height:
            update['height'] = self.height

        if self.width:
            update['width'] = self.width

        if self.height_banner:
            update['height_banner'] = self.height_banner

        if self.width_banner:
            update['width_banner'] = self.width_banner

        update['auto_reload'] = to_int(self.auto_reload)
        update['blinking'] = to_int(self.blinking)
        update['shake'] = to_int(self.shake)
        update['rating_division'] = to_int(self.rating_division, 1000)
        update['rating_hard_limit'] = self.rating_hard_limit
        update['blinking_reload'] = self.blinking_reload
        update['shake_reload'] = self.shake_reload
        update['shake_mouse'] = self.shake_mouse
        update['html_notification'] = self.html_notification
        update['plase_branch'] = self.plase_branch
        update['retargeting_branch'] = self.retargeting_branch
        update['disable_filter'] = self.disable_filter

        if self.cost:
            update['cost'] = self.cost
        if isinstance(self.non_relevant, dict) and 'action' in self.non_relevant and 'userCode' in self.non_relevant:
            update['nonRelevant'] = {'action': self.non_relevant['action'],
                                     'userCode': self.non_relevant['userCode']}
        update['lastModified'] = datetime.datetime.now()

        #Clean CSS
        update['css'] = ''
        update['css_banner'] = ''


        self.db.informer.update({'guid': self.guid},
                                {'$set': update}, upsert=True)
        InformerFtpUploader(self.guid).upload()
        MQ().informer_update(self.guid)

    def loadGuid(self, id):
        """ Загружает информер из MongoDB """
        if id is not None:
            mongo_record = self.db.informer.find_one({'guid': id})
            record = self.db.users.find_one({'login': mongo_record["user"]})
            self.guid = mongo_record['guid']
            self.guid_int = mongo_record.get('guid_int', uuid_to_long(self.guid))
            self.dynamic = mongo_record.get('dynamic', False)
            self.title = mongo_record['title']
            self.user_login = mongo_record["user"]
            if mongo_record.get("user_guid"):
                self.user_guid = mongo_record["user_guid"]
            else:
                record = self.user_by_login(self.user_login)
                self.user_guid = record.get('guid')
            self.user_guid_int = mongo_record.get("user_guid_int", uuid_to_long(self.user_guid))
            self.admaker = mongo_record.get('admaker')
            self.domain = mongo_record.get('domain')
            if mongo_record.get('domain_guid'):
                self.domain_guid = mongo_record.get('domain_guid')
            else:
                record = self.db.domain.find_one({'login': self.user_login})
                obj = record.get('domains', {})
                for k, v in obj.iteritems():
                    if v == self.domain:
                        self.domain_guid = k
                        break
            self.domain_guid_int = mongo_record.get('domain_guid_int', uuid_to_long(self.domain_guid))
            self.cost = mongo_record.get('cost', None)
            self.height = mongo_record.get('height')
            self.width = mongo_record.get('width')
            self.height_banner = mongo_record.get('height_banner')
            self.width_banner = mongo_record.get('width_banner')
            self.range_short_term = float(record.get('range_short_term', (100 / 100.0)))
            self.range_long_term = float(record.get('range_long_term', (0 / 100.0)))
            self.range_context = float(record.get('range_context', (0 / 100.0)))
            self.range_search = float(record.get('range_search', (100 / 100.0)))
            self.range_retargeting = float(record.get('range_retargeting', (100 / 100.0)))
            self.blinking = int(mongo_record.get('blinking', 0))
            self.shake = int(mongo_record.get('shake', 0))
            self.rating_division = int(mongo_record.get('rating_division', 1000))
            self.rating_hard_limit = bool(mongo_record.get('rating_hard_limit', False))
            self.html_notification = bool(mongo_record.get('html_notification', False))
            self.blinking_reload = bool(mongo_record.get('blinking_reload', False))
            self.shake_reload = bool(mongo_record.get('shake_reload', False))
            self.shake_mouse = bool(mongo_record.get('shake_mouse', False))
            self.plase_branch = bool(mongo_record.get('plase_branch', True))
            self.retargeting_branch = bool(mongo_record.get('retargeting_branch', True))
            self.disable_filter = bool(mongo_record.get('disable_filter', False))
            if 'nonRelevant' in mongo_record:
                self.non_relevant = {}
                self.non_relevant['action'] = \
                    mongo_record['nonRelevant'].get('action', 'social')
                self.non_relevant['userCode'] = \
                    mongo_record['nonRelevant'].get('userCode', '')


class InformerFtpUploader:
    """ Заливает необходимое для работы информера файлы на сервер раздачи
        статики:

        1. Javascript-загрузчик информера.
        2. Статическую заглушку с социальной рекламой на случай отказа GetMyAd.
    """

    def __init__(self, informer_id):
        """

        Args:
            informer_id:
        """
        self.informer_id = informer_id
        self.db = app_globals.db

    def upload(self):
        """ Заливает через FTP загрузчик и заглушку информера """
        self.upload_loader()

    def upload_loader(self):
        ' Заливает загрузчик информера '
        if config.get('informer_loader_ftp'):
            try:

                ftp = FTP(host=config.get('informer_loader_ftp'),
                          user=config.get('informer_loader_ftp_user'),
                          passwd=config.get('informer_loader_ftp_password'))
                ftp.cwd(config.get('informer_loader_ftp_path'))
                loader = StringIO.StringIO()
                loader.write(self._generate_informer_loader_json())
                loader.seek(0)
                ftp.storlines('STOR %s.json' % self.informer_id.lower(), loader)
                loader.close()
                loader = StringIO.StringIO()
                loader.write(self._generate_informer_loader_js())
                loader.seek(0)
                ftp.storlines('STOR %s.js' % self.informer_id.lower(), loader)
                ftp.quit()
                loader.close()
            except Exception, ex:
                logging.error(ex)
        else:
            logging.warning('informer_loader_ftp settings not set! '
                            'Check .ini file.')

    def uploadAll(self):
        """ Загружает на FTP скрипты для всех информеров """
        advertises = self.db.informer.find({}, {'guid': 1})
        prog = progressBar(0, advertises.count())
        i = 0
        for adv in advertises:
            i += 1
            prog.updateAmount(i)
            print "Saving informer %s... \t\t\t %s" % (adv['guid'], prog)
            InformerFtpUploader(adv['guid']).upload()

    def _generate_informer_loader_json(self):
        adv = self.db.informer.find_one({'guid': self.informer_id})
        if not adv:
            return json.dumps({'h': 'auto', 'w': 'auto', 'm': ''})

        last_modified = adv.get('lastModified')
        last_modified = last_modified.strftime("%Y%m%d%H%M%S")
        if adv.get('dynamic', False):
            return json.dumps({'h': 'auto', 'w': 'auto', 'm': last_modified})

        try:
            width = int(re.match('[0-9]+',
                        adv['admaker']['Main']['width']).group(0))
            height = int(re.match('[0-9]+',
                         adv['admaker']['Main']['height']).group(0))
        except:
            width = 'auto'
            height = 'auto'
        try:
            border = int(re.match('[0-9]+',
                         adv['admaker']['Main']['borderWidth']).group(0))
        except:
            border = 1
        width += border * 2
        height += border * 2
        return json.dumps({'h': height, 'w': width, 'm': last_modified})

    def _generate_informer_loader_js(self):
        adv = self.db.informer.find_one({'guid': self.informer_id})
        if not adv:
            return ""

        last_modified = adv.get('lastModified')
        last_modified = last_modified.strftime("%Y%m%d%H%M%S")
        if adv.get('dynamic', False):
            guid = adv.get('guid', '')
            script = (ur"""
            adsbyyottos.block_settings.cache['%(guid)s'] = {"h": %(height)s, "m": "%(last_modified)s", "w": %(width)s};
            """) % {'guid': guid, 'width': '"auto"', 'height': '"auto"', 'last_modified': last_modified}

            return """//<![CDATA[\n""" + minifier.minify(script.encode('utf-8'), mangle=False) + """\n//]]>"""

        try:
            guid = adv['guid']
            width = int(re.match('[0-9]+',
                        adv['admaker']['Main']['width']).group(0))
            height = int(re.match('[0-9]+',
                         adv['admaker']['Main']['height']).group(0))
        except:
            width = 0
            height = 0

        try:
            border = int(re.match('[0-9]+',
                         adv['admaker']['Main']['borderWidth']).group(0))
        except:
            border = 1
        width += border * 2
        height += border * 2

        script = (ur"""
        adsbyyottos.block_settings.cache['%(guid)s'] = {"h": %(height)s, "m": "%(last_modified)s", "w": %(width)s};
        """) % {'guid': guid, 'width': width, 'height': height, 'last_modified': last_modified}

        return """//<![CDATA[\n""" + minifier.minify(script.encode('utf-8'), mangle=False) + """\n//]]>"""


class InformerPattern:
    """ Рекламный информер (он же рекламный скрипт, рекламная выгрузка) """

    def __init__(self):
        """
        """
        self.guid = None
        self.admaker = None
        self.db = app_globals.db

    def save(self):
        """ Сохраняет информер, при необходимости создаёт """
        update = {}
        if self.guid:
            pass
        else:
            self.guid = str(uuid4()).lower()
            
        if self.admaker:
            update['admaker'] = self.admaker

        self.db.informer.patterns.update({'guid': self.guid},
                                       {'$set': update},
                                       upsert=True)

    def load(self, id):
        """

        Args:
            id:
        """
        raise NotImplementedError

    def loadGuid (self, id):
        """ Загружает информер из MongoDB """
        mongo_record = self.db.informer.patterns.find_one({'guid': id})
        self.guid = mongo_record['guid']
        self.guid_int = mongo_record['guid_int']
        self.title = mongo_record['title']
        self.user_login = mongo_record["user"]
        self.admaker = mongo_record.get('admaker')
        self.height = mongo_record.get('height')
        self.width = mongo_record.get('width')
        self.height_banner = mongo_record.get('height_banner')
        self.width_banner = mongo_record.get('width_banner')
