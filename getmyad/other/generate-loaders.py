#!/usr/bin/python
# encoding: utf-8
import StringIO
import json
import re
from ftplib import FTP

import pymongo
from slimit import minifier


def _generate_informer_loader_json(informer_id, db):
    adv = db.informer.find_one({'guid': informer_id})
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


def _generate_informer_loader_js(informer_id, db):
    adv = db.informer.find_one({'guid': informer_id})
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


def _generate_informer_loader_ssl(informer_id, db):
    ''' Возвращает код javascript-загрузчика информера '''
    adv = db.informer.find_one({'guid': informer_id})
    if not adv:
        return False
    try:
        guid = adv['guid']
        width = int(re.match('[0-9]+', adv['admaker']['Main']['width']).group(0))
        height = int(re.match('[0-9]+', adv['admaker']['Main']['height']).group(0))
    except:
        raise Exception("Incorrect size dimensions for informer %s" % informer_id)
    try:
        border = int(re.match('[0-9]+', adv['admaker']['Main']['borderWidth']).group(0))
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

            ;el.src = src + 'v1/pub?scr=' + adv.guid + '&mod=' + adv.lastModified;
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
            """) % {'guid': guid, 'width': width, 'height': height, 'lastModified': lastModified}

    return """//<![CDATA[\n""" + minifier.minify(script.encode('utf-8'), mangle=False) + """\n//]]>"""


def upload_all():
    # Параметры FTP для заливки загрузчиков информеров
    informer_loader_ftp = 'srv-3.yottos.com'
    informer_loader_ftp_user = 'cdn'
    informer_loader_ftp_password = '$www-app$'
    informer_loader_ftp_path = 'httpdocs/getmyad'
    informer_loader_ftp_path_new = 'httpdocs/block'
    db = pymongo.Connection(host='srv-5.yottos.com:27018,srv-9.yottos.com:27018,srv-5.yottos.com:27019').getmyad_db

    informers = [x['guid'] for x in db.informer.find({}, ['guid']).sort("lastModified", -1)]

    for informer in informers:
        ftp = FTP(host=informer_loader_ftp,
                  user=informer_loader_ftp_user,
                  passwd=informer_loader_ftp_password)
        ftp.cwd(informer_loader_ftp_path)
        print "Uploading %s" % informer
        loader = StringIO.StringIO()
        loader.write(_generate_informer_loader_ssl(informer, db))
        loader.seek(0)
        ftp.storlines('STOR %s.js' % informer, loader)
        ftp.quit()
        loader.close()

        ftp = FTP(host=informer_loader_ftp,
                  user=informer_loader_ftp_user,
                  passwd=informer_loader_ftp_password)
        ftp.cwd(informer_loader_ftp_path_new)
        print "Uploading %s" % informer
        loader = StringIO.StringIO()
        loader.write(_generate_informer_loader_json(informer, db))
        loader.seek(0)
        ftp.storlines('STOR %s.json' % informer, loader)
        loader.close()
        loader = StringIO.StringIO()
        loader.write(_generate_informer_loader_js(informer, db))
        loader.seek(0)
        ftp.storlines('STOR %s.js' % informer, loader)
        ftp.quit()
        loader.close()


if __name__ == '__main__':
    upload_all()
    print "Finished!"
    exit()
