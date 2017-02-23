# -*- coding: UTF-8 -*-
import hashlib as h
from binascii import crc32

from pylons import app_globals


class Offer(object):
    'Класс описывает рекламное предложение'

    def __init__(self, id, db=None):
        if db is None:
            self.db = app_globals.db_m
        else:
            self.db = db
        self.id = id.lower()
        self.id_int = long(crc32(self.id.encode('utf-8')) & 0xffffffff)
        self.title = ''
        self.price = ''
        self.url = ''
        self.image = None
        self.swf = None
        self.html = None
        self.description = ''
        self.date_added = None
        self.campaign = ''
        self.campaign_int = 0
        self.campaignTitle = ''
        self.uniqueHits = 1
        self.contextOnly = False
        self.retargeting = False
        self.keywords = []
        self.phrases = []
        self.exactly_phrases = []
        self.minus_words = []
        self.listAds = []
        self.category = 0
        self.isOnClick = True
        self.type = ''
        self.width = ''
        self.height = ''
        self.rating = 0.0
        self.full_rating = 0.0
        self.hash = ''
        self.cost = 0
        self.accountId = ''
        self.RetargetingID = ''
        self.Recommended = ''

    def offerHashes(self):
        print

    def createOfferHash(self):
        offerHash = {}
        offerHash['guid'] = self.id
        offerHash['guid_int'] = long(self.id_int)
        offerHash['title'] = self.title
        offerHash['url'] = self.url
        offerHash['campaignId'] = self.campaign
        offerHash['campaignId_int'] = self.campaign_int
        offerHash['cost'] = self.cost
        offerHash['price'] = self.price
        offerHash['dateAdded'] = self.date_added

        offerHash = str(h.md5(str(offerHash)).hexdigest())
        return offerHash

    def save(self):
        'Сохраняет предложение в базу данных'
        try:
            self.db.offer.update({'guid': self.id, 'guid_int': long(self.id_int)},
                                 {'$set': {'title': self._trim_by_words(self.title, 35),
                                           'price': self.price,
                                           'url': self.url,
                                           'image': self.image,
                                           'swf': self.swf,
                                           'html': self.html,
                                           'description': self._trim_by_words(self.description, 70),
                                           'dateAdded': self.date_added,
                                           'campaignId': self.campaign,
                                           'campaignId_int': long(self.campaign_int),
                                           'campaignTitle': self.campaignTitle,
                                           'uniqueHits': self.uniqueHits,
                                           'contextOnly': self.contextOnly,
                                           'retargeting': self.retargeting,
                                           'keywords': self.keywords,
                                           'phrases': self.phrases,
                                           'exactly_phrases': self.exactly_phrases,
                                           'minus_words': self.minus_words,
                                           'listAds': self.listAds,
                                           'category': long(self.category),
                                           'isOnClick': self.isOnClick,
                                           'type': self.type,
                                           'width': self.width,
                                           'height': self.height,
                                           'rating': self.rating,
                                           'full_rating': self.full_rating,
                                           'hash': self.hash,
                                           'cost': self.cost,
                                           'accountId': self.accountId,
                                           'RetargetingID': self.RetargetingID,
                                           'Recommended': self.Recommended
                                           }},
                                 upsert=True, safe=False)
        except Exception as e:
            print e

    def update(self):
        'Обнавляет предложение в базу данных'
        try:
            if self.image == "":
                self.db.offer.update({'guid': self.id, 'guid_int': long(self.id_int), 'campaignId': self.campaign,
                                      'campaignId_int': long(self.campaign_int)},
                                     {'$set': {'swf': self.swf,
                                               'html': self.html,
                                               'uniqueHits': self.uniqueHits,
                                               'contextOnly': self.contextOnly,
                                               'retargeting': self.retargeting,
                                               'listAds': self.listAds,
                                               'isOnClick': self.isOnClick,
                                               'type': self.type,
                                               'width': self.width,
                                               'height': self.height,
                                               'cost': self.cost,
                                               'accountId': self.accountId,
                                               'RetargetingID': self.RetargetingID,
                                               'Recommended': self.Recommended
                                               }},
                                     False)
            else:
                self.db.offer.update({'guid': self.id, 'guid_int': long(self.id_int), 'campaignId': self.campaign,
                                      'campaignId_int': long(self.campaign_int)},
                                     {'$set': {'image': self.image,
                                               'swf': self.swf,
                                               'html': self.html,
                                               'uniqueHits': self.uniqueHits,
                                               'contextOnly': self.contextOnly,
                                               'retargeting': self.retargeting,
                                               'listAds': self.listAds,
                                               'isOnClick': self.isOnClick,
                                               'type': self.type,
                                               'width': self.width,
                                               'height': self.height,
                                               'cost': self.cost,
                                               'accountId': self.accountId,
                                               'RetargetingID': self.RetargetingID,
                                               'Recommended': self.Recommended
                                               }},
                                     False)

        except Exception as e:
            print e

    def _trim_by_words(self, str, max_len):
        ''' Обрезает строку ``str`` до длины не более ``max_len`` с учётом слов '''
        if len(str) <= max_len:
            return str
        trimmed_simple = str[:max_len]
        trimmed_by_words = trimmed_simple.rpartition(' ')[0]
        return u'%s…' % (trimmed_by_words or trimmed_simple)
