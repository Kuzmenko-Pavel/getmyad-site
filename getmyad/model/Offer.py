# -*- coding: UTF-8 -*-
import hashlib as h
from binascii import crc32

from pylons import app_globals


class Offer(object):
    'Класс описывает рекламное предложение'

    __slots__ = ['db', 'id', 'id_int', 'title', 'price', 'url', 'image', 'description', 'date_added', 'campaign',
                 'campaign_int', 'campaignTitle', 'retargeting', 'rating', 'full_rating', 'hash', 'cost', 'accountId',
                 'RetargetingID', 'Recommended']

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
        self.description = ''
        self.date_added = None
        self.campaign = ''
        self.campaign_int = 0
        self.campaignTitle = ''
        self.retargeting = False
        self.rating = 0.0
        self.full_rating = 0.0
        self.hash = None
        self.cost = 0
        self.accountId = ''
        self.RetargetingID = ''
        self.Recommended = ''

    @property
    def createOfferHash(self):
        if self.hash is not None:
            return self.hash
        offerHash = {}
        offerHash['guid'] = self.id
        offerHash['guid_int'] = long(self.id_int)
        offerHash['title'] = self.title
        offerHash['description'] = self.description
        offerHash['url'] = self.url
        offerHash['campaignId'] = self.campaign
        offerHash['campaignId_int'] = self.campaign_int
        offerHash['cost'] = self.cost
        offerHash['price'] = self.price
        offerHash['dateAdded'] = self.date_added
        self.hash = str(h.md5(str(offerHash)).hexdigest())
        return self.hash

    def save(self):
        'Сохраняет предложение в базу данных'
        try:
            self.db.offer.update({'guid': self.id, 'guid_int': long(self.id_int)},
                                 {'$set': {'title': self._trim_by_words(self.title, 35),
                                           'price': self.price,
                                           'url': self.url,
                                           'image': self.image,
                                           'description': self._trim_by_words(self.description, 70),
                                           'dateAdded': self.date_added,
                                           'campaignId': self.campaign,
                                           'campaignId_int': long(self.campaign_int),
                                           'campaignTitle': self.campaignTitle,
                                           'retargeting': self.retargeting,
                                           'rating': self.rating,
                                           'full_rating': self.full_rating,
                                           'hash': self.hash,
                                           'cost': self.cost,
                                           'accountId': self.accountId,
                                           'RetargetingID': self.RetargetingID,
                                           'Recommended': self.Recommended
                                           }},
                                 upsert=True, w=1)
        except Exception as e:
            print e

    def update(self):
        'Обнавляет предложение в базу данных'
        try:
            if self.image == "":
                self.db.offer.update({'guid': self.id, 'guid_int': long(self.id_int), 'campaignId': self.campaign,
                                      'campaignId_int': long(self.campaign_int)},
                                     {'$set': {'retargeting': self.retargeting,
                                               'RetargetingID': self.RetargetingID,
                                               'Recommended': self.Recommended
                                               }},
                                     upsert=False, w=1)
            else:
                self.db.offer.update({'guid': self.id, 'guid_int': long(self.id_int), 'campaignId': self.campaign,
                                      'campaignId_int': long(self.campaign_int)},
                                     {'$set': {'image': self.image,
                                               'retargeting': self.retargeting,
                                               'RetargetingID': self.RetargetingID,
                                               'Recommended': self.Recommended
                                               }},
                                     upsert=False, w=1)

        except Exception as e:
            print e

    def _trim_by_words(self, str, max_len):
        ''' Обрезает строку ``str`` до длины не более ``max_len`` с учётом слов '''
        if len(str) <= max_len:
            return str
        trimmed_simple = str[:max_len]
        trimmed_by_words = trimmed_simple.rpartition(' ')[0]
        return u'%s…' % (trimmed_by_words or trimmed_simple)
