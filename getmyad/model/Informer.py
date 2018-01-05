# -*- coding: UTF-8 -*-
from ftplib import FTP
from uuid import uuid1
import StringIO
import datetime
import logging
from binascii import crc32
import json

from getmyad.lib.helpers import progressBar
from getmyad.lib.admaker_validator import validate_admaker
from getmyad.lib.template_convertor import js2mako
from getmyad.model import mq
from pylons import config, app_globals
import mako.template
import re
from slimit import minifier


class Informer:
    """ Рекламный информер (он же рекламный скрипт, рекламная выгрузка) """

    def __init__(self):
        """

        """
        self.guid = None
        self.guid_int = 0
        self.dynamic = False
        self.title = None
        self.admaker = None
        self.css = None
        self.css_banner = None
        self.user_login = None
        self.non_relevant = None
        self.domain = None
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
        self.db = app_globals.db


    def save(self):
        """ Сохраняет информер, при необходимости создаёт """
        update = {}
        if self.guid:
            self.guid_int = long(crc32(self.guid.encode('utf-8')) & 0xffffffff)
        else:
            self.guid = str(uuid1()).lower()
            self.guid_int = long(crc32(self.guid.encode('utf-8')) & 0xffffffff)
            if not self.user_login:
                raise ValueError('User login must be specified when creating '
                                 'informer!')
            update['user'] = self.user_login
        if self.user_login is not None:
            record = self.db.users.find_one({'login': self.user_login})
            self.range_short_term = float(record.get('range_short_term', (100 / 100.0)))
            update['range_short_term'] = self.range_short_term
            self.range_long_term = float(record.get('range_long_term', (0 / 100.0)))
            update['range_long_term'] = self.range_long_term
            self.range_context = float(record.get('range_context', (0 / 100.0)))
            update['range_context'] = self.range_context
            self.range_search = float(record.get('range_search', (100 / 100.0)))
            update['range_search'] = self.range_search
            self.range_retargeting = float(record.get('range_retargeting', (100 / 100.0)))
            update['retargeting_capacity'] = self.range_retargeting
        else:
            self.range_short_term = (100 / 100.0) 
            self.range_long_term = (0 / 100.0)
            self.range_context = (0 / 100.0)
            self.range_search = (100 / 100.0)
            self.range_retargeting = (100 / 100.0)
            update['user'] = self.user_login
            update['range_short_term'] = self.range_short_term
            update['range_long_term'] = self.range_long_term
            update['range_context'] = self.range_context
            update['range_search'] = self.range_search
            update['retargeting_capacity'] = self.range_retargeting

        update['dynamic'] = self.dynamic
        if self.title:
            update['title'] = self.title
        if self.admaker:
            update['admaker'] = self.admaker
        if self.css:
            update['css'] = self.css
        else:
            update['css'] = self.admaker_options_to_css(self.admaker)
        if self.css_banner:
            update['css_banner'] = self.css_banner
        else:
            update['css_banner'] = self.admaker_options_to_css_banner(self.admaker)
        if self.domain:
            update['domain'] = self.domain
        if self.height:
            update['height'] = self.height
        if self.width:
            update['width'] = self.width
        if self.height_banner:
            update['height_banner'] = self.height_banner
        if self.width_banner:
            update['width_banner'] = self.width_banner
        if isinstance(self.auto_reload, int):
            update['auto_reload'] = self.auto_reload
        elif (isinstance(self.auto_reload, str) and self.auto_reload.isdigit()):
            update['auto_reload'] = int(self.auto_reload)
        elif (isinstance(self.auto_reload, unicode) and self.auto_reload.isdigit()):
            update['auto_reload'] = int(self.auto_reload)
        else:
            update['auto_reload'] = 0

        if isinstance(self.blinking, int):
            update['blinking'] = self.blinking
        elif (isinstance(self.blinking, str) and self.blinking.isdigit()):
            update['blinking'] = int(self.blinking)
        elif (isinstance(self.blinking, unicode) and self.blinking.isdigit()):
            update['blinking'] = int(self.blinking)
        else:
            update['blinking'] = 0

        if isinstance(self.shake, int):
            update['shake'] = self.shake
        elif (isinstance(self.shake, str) and self.shake.isdigit()):
            update['shake'] = int(self.shake)
        elif (isinstance(self.shake, unicode) and self.shake.isdigit()):
            update['shake'] = int(self.shake)
        else:
            update['shake'] = 0

        if isinstance(self.rating_division, int):
            update['rating_division'] = self.rating_division
        elif (isinstance(self.rating_division, str) and self.rating_division.isdigit()):
            update['rating_division'] = int(self.rating_division)
        elif (isinstance(self.rating_division, unicode) and self.rating_division.isdigit()):
            update['rating_division'] = int(self.rating_division)
        else:
            update['rating_division'] = 1000
        update['blinking_reload'] = self.blinking_reload
        update['shake_reload'] = self.shake_reload
        update['shake_mouse'] = self.shake_mouse
        update['html_notification'] = self.html_notification
        update['plase_branch'] = self.plase_branch
        update['retargeting_branch'] = self.retargeting_branch
        if self.cost:
            update['cost'] = self.cost
        if isinstance(self.non_relevant, dict) and 'action' in self.non_relevant and 'userCode' in self.non_relevant:
            update['nonRelevant'] = {'action': self.non_relevant['action'],
                                     'userCode': self.non_relevant['userCode']}
        update['lastModified'] = datetime.datetime.now()

        self.db.informer.update({'guid': self.guid, 'guid_int': long(self.guid_int)},
                                       {'$set': update},
                                       upsert=True)
        InformerFtpUploader(self.guid).upload()
        mq.MQ().informer_update(self.guid)

    def load(self, id):
        """

        Args:
            id:
        """
        raise NotImplementedError

    def loadGuid (self, id):
        """ Загружает информер из MongoDB """
        if id is not None:
            mongo_record = self.db.informer.find_one({'guid': id})
            record = self.db.users.find_one({'login': mongo_record["user"]})
            self.guid = mongo_record['guid']
            self.guid_int = mongo_record['guid_int']
            self.dynamic = mongo_record.get('dynamic', False)
            self.title = mongo_record['title']
            self.user_login = mongo_record["user"]
            self.admaker = mongo_record.get('admaker')
            self.css = mongo_record.get('css')
            self.css_banner = mongo_record.get('css_banner')
            self.domain = mongo_record.get('domain')
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
            self.html_notification = bool(mongo_record.get('html_notification', False))
            self.blinking_reload = bool(mongo_record.get('blinking_reload', False))
            self.shake_reload = bool(mongo_record.get('shake_reload', False))
            self.shake_mouse = bool(mongo_record.get('shake_mouse', False))
            self.plase_branch = bool(mongo_record.get('plase_branch', True))
            self.retargeting_branch = bool(mongo_record.get('retargeting_branch', True))
            if 'nonRelevant' in mongo_record:
                self.non_relevant = {}
                self.non_relevant['action'] = \
                    mongo_record['nonRelevant'].get('action', 'social')
                self.non_relevant['userCode'] = \
                    mongo_record['nonRelevant'].get('userCode', '')

    @staticmethod
    def load_from_mongo_record(mongo_record):
        """ Загружает информер из записи MongoDB """
        informer = Informer()
        informer.guid = mongo_record['guid']
        informer.guid_int = mongo_record['guid_int']
        informer.dynamic = mongo_record.get('dynamic', False)
        informer.title = mongo_record['title']
        informer.user_login = mongo_record["user"]
        db = app_globals.db
        record = db.users.find_one({'login': mongo_record["user"]})
        informer.admaker = mongo_record.get('admaker')
        informer.css = mongo_record.get('css')
        informer.css_banner = mongo_record.get('css_banner')
        informer.domain = mongo_record.get('domain')
        informer.cost = mongo_record.get('cost', None)
        informer.height = mongo_record.get('height')
        informer.width = mongo_record.get('width')
        informer.height_banner = mongo_record.get('height_banner')
        informer.width_banner = mongo_record.get('width_banner')
        informer.range_short_term = float(record.get('range_short_term', (100 / 100.0)))
        informer.range_long_term = float(record.get('range_long_term', (0 / 100.0)))
        informer.range_context = float(record.get('range_context', (0 / 100.0)))
        informer.range_search = float(record.get('range_search', (100 / 100.0)))
        informer.range_retargeting = float(record.get('range_retargeting', (100 / 100.0)))
        informer.blinking = int(mongo_record.get('blinking', 0))
        informer.shake = int(mongo_record.get('shake', 0))
        informer.rating_division = int(mongo_record.get('rating_division', 1000))
        informer.html_notification = bool(mongo_record.get('html_notification', False))
        informer.blinking_reload = bool(mongo_record.get('blinking_reload', True))
        informer.shake_reload = bool(mongo_record.get('shake_reload', True))
        informer.shake_mouse = bool(mongo_record.get('shake_mouse', True))
        informer.plase_branch = bool(mongo_record.get('plase_branch', True))
        informer.retargeting_branch = bool(mongo_record.get('retargeting_branch', True))
        if 'nonRelevant' in mongo_record:
            informer.non_relevant = {}
            informer.non_relevant['action'] = \
                mongo_record['nonRelevant'].get('action', 'social')
            informer.non_relevant['userCode'] = \
                mongo_record['nonRelevant'].get('userCode', '')
        return informer

    def admaker_options_to_css(self, options):
        """ Создаёт строку CSS из параметров Admaker """

        def parseInt(value):
            ''' Пытается выдрать int из строки.
                
                Например, для "128px" вернёт 128. '''
            try:
                return re.findall("\\d+", value)[0]
            except IndexError:
                return 0
        options = validate_admaker(options)
        template_name = '/advertise_style_template.mako.html'
        src = app_globals.mako_lookup.get_template(template_name)\
                .source.replace('<%text>', '').replace('</%text>', '')
        template = mako.template.Template(
            text=js2mako(src), 
            format_exceptions=True)
        return template.render_unicode(parseInt=parseInt, **options)

    def admaker_options_to_css_banner(self, options):
        """ Создаёт строку CSS Banner из параметров Admaker """

        def parseInt(value):
            ''' Пытается выдрать int из строки.
                
                Например, для "128px" вернёт 128. '''
            try:
                return re.findall("\\d+", value)[0]
            except IndexError:
                return 0

        options = validate_admaker(options)
        template_name = '/advertise_style_template_banner.mako.html'
        src = app_globals.mako_lookup.get_template(template_name)\
                .source.replace('<%text>', '').replace('</%text>', '')
        template = mako.template.Template(
            text=js2mako(src), 
            format_exceptions=True)
        return template.render_unicode(parseInt=parseInt, **options)
#        return minify_css( template.render_unicode(parseInt=h.parseInt, **opt) )


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


def minify_css(css):
    """

    Args:
        css:

    Returns:

    """
    # remove comments - this will break a lot of hacks :-P
    css = re.sub( r'\s*/\*\s*\*/', "$$HACK1$$", css ) # preserve IE<6 comment hack
    css = re.sub( r'/\*[\s\S]*?\*/', "", css )
    css = css.replace( "$$HACK1$$", '/**/' ) # preserve IE<6 comment hack
    
    # url() doesn't need quotes
    css = re.sub( r'url\((["\'])([^)]*)\1\)', r'url(\2)', css )
    
    # spaces may be safely collapsed as generated content will collapse them anyway
    css = re.sub( r'\s+', ' ', css )
    
    # shorten collapsable colors: #aabbcc to #abc
    css = re.sub( r'#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(\s|;)', r'#\1\2\3\4', css )
    
    # fragment values can loose zeros
    css = re.sub( r':\s*0(\.\d+([cm]m|e[mx]|in|p[ctx]))\s*;', r':\1;', css )
    
    result = []
    for rule in re.findall( r'([^{]+){([^}]*)}', css ):
    
        # we don't need spaces around operators
        selectors = [re.sub( r'(?<=[\[\(>+=])\s+|\s+(?=[=~^$*|>+\]\)])', r'', selector.strip() ) for selector in rule[0].split( ',' )]
    
        # order is important, but we still want to discard repetitions
        properties = {}
        porder = []
        for prop in re.findall( '(.*?):(.*?)(;|$)', rule[1] ):
            key = prop[0].strip().lower()
            if key not in porder: porder.append( key )
            properties[ key ] = prop[1].strip()
    
        # output rule if it contains any declarations
        if properties:
            result.append( "%s{%s}" % ( ','.join( selectors ), ''.join(['%s:%s;' % (key, properties[key]) for key in porder])[:-1] ))
    return "\n".join(result)



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
            self.guid = str(uuid1()).lower()
            
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

    @staticmethod
    def load_from_mongo_record(mongo_record):
        """ Загружает информер из записи MongoDB """
        informer = InformerPattern()
        informer.guid = mongo_record['guid']
        informer.title = mongo_record['title']
        db = app_globals.db
        informer.admaker = mongo_record.get('admaker')
        informer.height = mongo_record.get('height')
        informer.width = mongo_record.get('width')
        informer.height_banner = mongo_record.get('height_banner')
        informer.width_banner = mongo_record.get('width_banner')
        return informer
