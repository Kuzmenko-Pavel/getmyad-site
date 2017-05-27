# -*- coding: UTF-8 -*-
from ftplib import FTP
from uuid import uuid1
import StringIO
import datetime
import logging
from binascii import crc32
import json

from getmyad.config.social_ads import social_ads
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
                                       upsert=True,
                                       safe=True)
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
        self.upload_reserve()

    def upload_loader(self):
        ' Заливает загрузчик информера '
        if config.get('informer_loader_ftp'):
            try:
                ftp = FTP(host=config.get('informer_loader_ftp'),
                          user=config.get('informer_loader_ftp_user'),
                          passwd=config.get('informer_loader_ftp_password'))
                ftp.cwd(config.get('informer_loader_ftp_path'))
                loader = StringIO.StringIO()
                loader.write(self._generate_informer_loader_ssl())
                loader.seek(0)
                ftp.storlines('STOR %s.js' % self.informer_id.lower(), loader)
                ftp.quit()
                loader.close()
            except Exception, ex:
                logging.error(ex)
            try:

                ftp = FTP(host=config.get('informer_loader_ftp'),
                          user=config.get('informer_loader_ftp_user'),
                          passwd=config.get('informer_loader_ftp_password'))
                ftp.cwd(config.get('informer_loader_ftp_path_new'))
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

    def upload_reserve(self):
        ' Заливает заглушку для информера '
        if config.get('reserve_ftp'):
            try:
                ftp = FTP(config.get('reserve_ftp'))
                ftp.login(config.get('reserve_ftp_user'),
                          config.get('reserve_ftp_password'))
                ftp.cwd(config.get('reserve_ftp_path'))
                data = StringIO.StringIO()
                data.write(self._generate_social_ads().encode('utf-8'))
                data.seek(0)
                ftp.storlines('STOR emergency-%s.html' % self.informer_id,
                              data)
                ftp.quit()
                data.close()
            except Exception, ex:
                logging.error(ex)
        else:
            logging.warning('reserve_ftp settings not set! Check .ini file.')

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
        try:
            width = int(re.match('[0-9]+',
                        adv['admaker']['Main']['width']).group(0))
            height = int(re.match('[0-9]+',
                         adv['admaker']['Main']['height']).group(0))
        except:
            raise Exception("Incorrect size dimensions for informer %s" %
                             self.informer_id)
        try:
            border = int(re.match('[0-9]+',
                         adv['admaker']['Main']['borderWidth']).group(0))
        except:
            border = 1
        width += border * 2
        height += border * 2
        last_modified = adv.get('lastModified')
        last_modified = last_modified.strftime("%Y%m%d%H%M%S")

        return json.dumps({'h': height, 'w': width, 'm': last_modified})

    def _generate_informer_loader_js(self):
        adv = self.db.informer.find_one({'guid': self.informer_id})
        if not adv:
            return ""
        try:
            guid = adv['guid']
            width = int(re.match('[0-9]+',
                        adv['admaker']['Main']['width']).group(0))
            height = int(re.match('[0-9]+',
                         adv['admaker']['Main']['height']).group(0))
        except:
            raise Exception("Incorrect size dimensions for informer %s" %
                             self.informer_id)
        try:
            border = int(re.match('[0-9]+',
                         adv['admaker']['Main']['borderWidth']).group(0))
        except:
            border = 1
        width += border * 2
        height += border * 2
        last_modified = adv.get('lastModified')
        last_modified = last_modified.strftime("%Y%m%d%H%M%S")
        script = (ur"""
        adsbyyottos.block_settings.cache['%(guid)s'] = {"h": %(height)s, "m": "%(last_modified)s", "w": %(width)s};
        """) % {'guid': guid, 'width': width, 'height': height, 'last_modified': last_modified}

        return """//<![CDATA[\n""" + minifier.minify(script.encode('utf-8'), mangle=False) + """\n//]]>"""

    def _generate_informer_loader_ssl(self):
        ''' Возвращает код javascript-загрузчика информера '''
        adv = self.db.informer.find_one({'guid': self.informer_id})
        if not adv:
            return False
        try:
            guid = adv['guid']
            width = int(re.match('[0-9]+',
                        adv['admaker']['Main']['width']).group(0))
            height = int(re.match('[0-9]+',
                         adv['admaker']['Main']['height']).group(0))
        except:
            raise Exception("Incorrect size dimensions for informer %s" %
                             self.informer_id)
        try:
            border = int(re.match('[0-9]+',
                         adv['admaker']['Main']['borderWidth']).group(0))
        except:
            border = 1
        width += border * 2
        height += border * 2
        lastModified = adv.get('lastModified')
        lastModified = lastModified.strftime("%Y%m%d%H%M%S")
        script = (ur"""
        if (typeof Date.now() === 'undefined') {
          Date.now = function () { 
                return new Date(); 
        }
        }
        var isElementInViewport =  function(el,scrollCounter) {
              var top = el.offsetTop ; 
              var left = el.offsetLeft ; 
              var width = el.offsetWidth ; 
              var height = el.offsetHeight ; 
              var pageYOffset;
              var pageXOffset;
              var YOffset = 0;
              var XOffset = 0;
              var innerWidth;
              var innerHeight;
                if (typeof window.innerWidth != 'undefined')
                {
                    innerWidth = window.innerWidth;
                    innerHeight = window.innerHeight;
                }
                else if (typeof document.documentElement != 'undefined' && typeof document.documentElement.clientWidth != 'undefined' && document.documentElement.clientWidth != 0)
                {
                    innerWidth = document.documentElement.clientWidth;
                    innerHeight = document.documentElement.clientHeight;
                }
                else
                {
                    innerWidth = document.getElementsByTagName('body')[0].clientWidth;
                    innerHeight = document.getElementsByTagName('body')[0].clientHeight;
                }
              if(typeof window.pageYOffset!= 'undefined'){
                    pageYOffset = window.pageYOffset;
                    pageXOffset = window.pageXOffset;
              }
              else
              {
                    pageYOffset = document.documentElement.scrollTop;
                    pageXOffset = document.documentElement.scrollLeft;
              } 
              while ( el.offsetParent )  { 
                el = el.offsetParent ; 
                top += el.offsetTop ; 
                left += el.offsetLeft ; 
              }
              if (scrollCounter > 1)
                {
                   YOffset = (pageYOffset/scrollCounter);
                   XOffset = (pageXOffset/scrollCounter); 
                }
              return  ( 
                top <  ( pageYOffset + innerHeight + YOffset )  && 
                left <  ( pageXOffset+ innerWidth + XOffset )  && 
                ( top + height ) > pageYOffset && 
                ( left + width ) > pageXOffset
               );
            };
        var onVisibility = function(el, callback) {
            var old_visible = false;
            var scrollCounter = 0;
            return function () {
                if (!old_visible)
                {
                    var visible = isElementInViewport(el,scrollCounter)
                    scrollCounter++;
                    if (visible != old_visible) {
                        old_visible = visible;
                        render = true;
                        if (typeof callback == 'function') {
                            callback();
                        }
                    }
                }
            }
        };
        var adv = {'guid':'%(guid)s',
        'width':'%(width)spx', 'height':'%(height)spx',
        'lastModified': '%(lastModified)s',
        'request':'initial'};
        var src = 'https://rg.yottos.com/';
        var lul = src + 'bl.js?';
        ;var rand = Math.floor(Math.random() * 1000000);
        ;var iframe_id = 'yottos' + rand;
        try {
            ;var el = document.createElement('<iframe name='+ iframe_id +'>');
        } catch (ex) {
            ;var el = document.createElement("iframe");
            ;el.name = iframe_id;
        }
        ;el.id = iframe_id;
        ;el.style.width = adv.width;
        ;el.marginHeight = '0px';
        ;el.marginWidth = '0px';
        ;el.style.height = adv.height;
        ;el.style.border = '0px';
        ;el.scrolling='no';
        ;el.frameBorder='0';
        ;el.allowtransparency='true';
        var yt_temp_adv_name = adv.guid.replace(/-/g, '');
        var name_el = window[yt_temp_adv_name].shift();
        var div_el = document.getElementById(name_el);

        ;el.src = src + 'block?scr=' + adv.guid + '&mod=' + adv.lastModified;
        var moveShake = function(iframe)
        {
            var old_timeStamp = 0;
            var sequence = [3,4,6,10,4,3,2,7,10,5,3,5,4,10,3,4,3,2];
            var sequence_w = sequence.slice();
            return function(e)
            {
                var timeStamp = e.timeStamp;
                var old_sequence_w = sequence_w.slice();
                var step = sequence_w.pop();
                if (step == 'undefined')
                {
                    step = 2;
                    sequence_w = sequence.slice();
                }
                if ((timeStamp/1000 - old_timeStamp/1000) > step)
                {
                    old_timeStamp = timeStamp;
                    if (iframe.contentWindow.postMessage)
                    {
                        iframe.contentWindow.postMessage('move','*');
                    }
                }
                else
                {
                    sequence_w = old_sequence_w.slice();
                }
            };
        };
        var sq = function(obj)
        {
            var str = [];
            for(var p in obj)
            {
                str.push(p + "=" + obj[p]);
            }
            return str.join("&");
        };
        delete adv['width'];
        delete adv['height'];
        delete adv['lastModified'];
        if (div_el != null){
            (function(name_el, el, adv) {
            var script = document.createElement('script');
            script.async=true;
            script.charset='UTF-8';
            script.type = 'text/javascript';
            adv.rand = Math.floor(Math.random() * 1000000);
            script.src = lul + sq(adv);
            script.id = 'yt' + adv.rand;
            var div_el = document.getElementById(name_el);
            ;div_el.appendChild(el);
            ;div_el.appendChild(script);
            ;var frame_el = document.getElementById(el.id);
            ;var handler = moveShake(frame_el);
            if (window.addEventListener) {
                addEventListener('mousemove', handler, false); 
            } else if (window.attachEvent)  {
                attachEvent('mousemove', handler);
            }
            var handler2 = onVisibility(frame_el, function() {
                    var script = document.createElement('script');
                    script.async=true;
                    script.charset='UTF-8';
                    script.type = 'text/javascript';
                    adv.rand = Math.floor(Math.random() * 1000000);
                    adv.request = 'complite';
                    script.src = lul + sq(adv);
                    script.id = 'yt' + adv.rand;
                    ;div_el.appendChild(script);
            });
            handler2();
            if (window.addEventListener) {
                addEventListener('scroll', handler2, false); 
                addEventListener('resize', handler2, false); 
            } else if (window.attachEvent)  {
                attachEvent('onscroll', handler2);
                attachEvent('onresize', handler2);
            }
            })(name_el, el, adv);
        }
        else{
            (function(name_el, el, adv) {
                  window.onload = function() {
                    var div_el = document.getElementById(name_el);
                    if (div_el != null){
                        var script = document.createElement('script');
                        script.async=true;
                        script.charset='UTF-8';
                        script.type = 'text/javascript';
                        adv.rand = Math.floor(Math.random() * 1000000);
                        script.src = lul + sq(adv);
                        script.id = 'yt' + adv.rand;
                        ;div_el.appendChild(el);
                        ;div_el.appendChild(script);
                        ;var frame_el = document.getElementById(el.id);
                        ;var handler = moveShake(frame_el);
                        if (window.addEventListener) {
                            addEventListener('mousemove', handler, false); 
                        } else if (window.attachEvent)  {
                            attachEvent('mousemove', handler);
                        }
                        var handler2 = onVisibility(frame_el, function() {
                            var script = document.createElement('script');
                            script.async=true;
                            script.charset='UTF-8';
                            script.type = 'text/javascript';
                            adv.rand = Math.floor(Math.random() * 1000000);
                            adv.request = 'complite';
                            script.src = lul + sq(adv);
                            script.id = 'yt' + adv.rand;
                            ;div_el.appendChild(script);
                        });
                        handler2();
                        if (window.addEventListener) {
                            addEventListener('scroll', handler2, false); 
                            addEventListener('resize', handler2, false); 
                        } else if (window.attachEvent)  {
                            attachEvent('onscroll', handler2);
                            attachEvent('onresize', handler2);
                        }
                    }
                };
            })(name_el, el, adv);
        }
        """) % {'guid':guid, 'width':width, 'height':height, 'lastModified':lastModified}
        
        return """//<![CDATA[\n""" +  minifier.minify(script.encode('utf-8') , mangle=False) + """\n//]]>"""
        #return """//<![CDATA[\n""" + script.encode('utf-8') + """\n//]]>"""
        #eturn script.encode('utf-8')



    def _generate_social_ads(self):
        ''' Возвращает HTML-код заглушки с социальной рекламой,
            которая будет показана при падении сервиса
        '''
        inf = self.db.informer.find_one({'guid': self.informer_id})
        if not inf:
            return

        try:
            items_count = int(inf['admaker']['Main']['itemsNumber'])
        except:
            items_count = 0

        offers = ''
        for i in xrange(0, items_count):
            adv = social_ads[i % len(social_ads)]

            offers += ('''<div class="advBlock"><a class="advHeader" href="%(url)s" target="_blank">''' +
                       '''%(title)s</a><a class="advDescription" href="%(url)s" target="_blank">''' +
                       '''%(description)s</a><a class="advCost" href="%(url)s" target="_blank"></a>''' +
                       '''<a href="%(url)s" target="_blank"><img class="advImage" src="%(img)s" alt="%(title)s"/></a></div>'''
                       ) % {'url': adv['url'], 'title': adv['title'], 'description': adv['description'], 'img': adv['image']}
        return '''
<html><head><META http-equiv="Content-Type" content="text/html; charset=utf-8"><meta name="robots" content="nofollow" /><style type="text/css">html, body { padding: 0; margin: 0; border: 0; }</style><!--[if lte IE 6]><script type="text/javascript" src="//cdn.yottos.com/getmyad/supersleight-min.js"></script><![endif]-->
%(css)s
</head>
<body>
<div id='mainContainer'><div id="ads" style="position: absolute; left:0; top: 0">
%(offers)s
</div><div id='adInfo'><a href="https://yottos.com" target="_blank"></a></div>
</body>
</html>''' % {'css': inf.get('css'), 'offers': offers}





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
                                       upsert=True,
                                       safe=True)

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
