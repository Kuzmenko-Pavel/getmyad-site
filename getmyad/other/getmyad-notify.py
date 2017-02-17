#!/usr/bin/python
# encoding: utf-8

import sys
import logging
import xmlrpclib

# Путь и имя log-файла
LOG_FILE = r'g:\www\log\getmyad-notify.log'

# Путь XML-RPC GetMyAd
GETMYAD_RPC = 'http://getmyad.vsrv-1.2.yottos.com/rpc'

def process():
    if len(sys.argv) <> 3:
        logging.debug("Invalid usage. sys.argv = %s" % sys.argv)
        print "Usage: getmyad-notify.py message campaign_id"
        exit()
    
    msg = sys.argv[1]
    id = sys.argv[2]
    
    try:
        server = xmlrpclib.ServerProxy(GETMYAD_RPC)
        if msg == 'campaign.start':
            logging.info('calling xml-rpc %s(%s)' % (msg, id))
            response = server.campaign.start(id)
        elif msg == 'campaign.stop':
            logging.info('calling xml-rpc %s(%s)' % (msg, id))
            response = server.campaign.stop(id)
        elif msg == 'campaign.update':
            logging.info('calling xml-rpc %s(%s)' % (msg, id))
            response = server.campaign.update(id)
        elif msg == 'informer.update':
            logging.info('calling xml-rpc %s(%s)' % (msg, id))
            response = server.informer.update(id)
        else:
            logging.warning('Unknown method %s with argument %s' % (msg, id))
            exit(1)
        if response:
            logging.info("Server response: %s" % response)
    except Exception, ex:
        logging.error('Exception: %s' % ex)

if __name__ == '__main__':
    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format="%(asctime)s - %(levelname)s\t %(message)s")
    process()