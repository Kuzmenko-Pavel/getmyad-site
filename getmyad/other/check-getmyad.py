# coding: utf-8
''' Проверяет работоспособность GetMyAd
'''

LOG_FILE = 'check-getmyad.log'

from time import time
import logging
import urllib2

import simplejson as json
import pymongo
from amqplib import client_0_8 as amqp

urls = [
#       ('Balancer', 'http://getmyad.vsrv-3.2.yottos.com/adshow.fcgi?scr=3402B070-7881-11DF-A153-0015175ECad8&test=true&country=UA&show=json'),
        ('vsrv-1.2', 'http://rg.1.2.yottos.com/adshow.fcgi?scr=3402B070-7881-11DF-A153-0015175ECad8&test=true&country=UA&show=json'),
#       ('vsrv-1.3', 'http://rg.1.3.yottos.com/adshow.fcgi?scr=3402B070-7881-11DF-A153-0015175ECad8&test=true&country=UA&show=json'),
        ('rg', 'http://rg.yottos.com/adshow.fcgi?scr=3402B070-7881-11DF-A153-0015175ECad8&test=true&country=UA&show=json')]

mongo_hosts = ['yottos.com',
               'vsrv-1.2.yottos.com:27018',
#               'vsrv-1.3.yottos.com:27018'
              ]

rabbitmq_hosts = ['vsrv-1.2.yottos.com',
#                 'vsrv-1.3.yottos.com'
                 ]

def check_getmyad_adshow(informer_url):
    start = time()
    
    # Пытаемся открыть информер
    try:
        f = urllib2.urlopen(informer_url)
        content = f.read()
        informer = json.loads(content)
    except urllib2.URLError as ex:
        return {'result': 'error',
                'description': 'Error opening informer url %s' % informer_url,
                'exception': ex}
    except json.JSONDecodeError as ex:
        return {'result': 'error',
                'description': 'Error parsing informer json for %s' % informer_url,
                'exception': ex,
                'content': content}

#    try:
#        for offer in informer:
#            # Пытаемся перейти по ссылке
#            redirect_script = urllib2.urlopen(offer['url']).read()
#            assert 'window.location.replace' in redirect_script, "Incorrect redirect script"
#            
#            # Убеждаемся, что ссылка перенаправления не пустая
#            redirect_url = re.findall("window.location.replace\('(.*)'\)", redirect_script)
#            assert redirect_url, "Incorrect or empty redirect link"
#          
#    except Exception as ex:
#        raise
       
    elapsed = time() - start
    return {'result': 'ok', 'elapsed': elapsed}
    
    
def check_services():
    ''' Проверка работоспособности различных служб: базы данных, очереди сообщений и т.д. '''
    result = []
    
    # MongoDB
    for host in mongo_hosts:
        print "Checking MongoDB at %s:" % host,
        try:
            pymongo.Connection(host=host)
        except pymongo.errors.AutoReconnect as ex:
            r = {'service': 'mongo@%s' % host,
                 'result': 'error',
                 'exception': ex,
                 'description': 'Error connecting to mongo host %s' % host}
        else:
            r = {'service': 'mongo@%s' % host, 'result': 'ok'}
        result.append(r)
        print r
            
    # RabbitMQ
    for host in rabbitmq_hosts:
        print "Checking RabbitMQ at %s " % host, 
        try:
            amqp.Connection(host=host)
        except Exception as ex:
            r = {'service': 'rabbitmq@%s' % host,
                 'result': 'error',
                 'exception': ex,
                 'description': 'Error connecting to RabbitMQ host %s' % host}
        else:
             r = {'service': 'rabbitmq@%s' % host, 'result': 'ok'}
        result.append(r)
        print r
    
    return result
    
    
if __name__ == '__main__':
    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG,
                        format="%(asctime)s - %(levelname)s\t %(message)s")
    logging.info("------------------------- checks started...")

    services_result = check_services()
    for r in services_result:
        if r.get('result') <> 'ok':
            logging.error(r)
    
    for url in urls:
        try:
            result = check_getmyad_adshow(url[1])
        except Exception as ex:
            result = {'result': 'error', 'exception': ex}
            
        if result.get('result') <> 'ok':
            logging.error(result)
            
        print "Checking %s: %s" % (url[0], result)
