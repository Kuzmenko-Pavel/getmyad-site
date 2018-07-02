# -*- coding: UTF-8 -*-
import hashlib

import pymongo

from getmyad.lib.helpers import uuid_to_long


class Offer(object):
    'Класс описывает рекламное предложение'

    __slots__ = ['id', 'id_int', 'title', 'price', 'url', 'image', 'description', 'campaign',
                 'campaign_int', 'campaignTitle', 'retargeting', '_hash', 'cost', 'accountId',
                 'RetargetingID', 'Recommended', '_image_hash', 'logo']

    def __init__(self, id):
        self.id = id.lower()
        self.id_int = uuid_to_long(self.id.encode('utf-8'))
        self.title = ''
        self.price = ''
        self.url = ''
        self.image = ''
        self.logo = ''
        self.description = ''
        self.campaign = ''
        self.campaign_int = 0
        self.campaignTitle = ''
        self.retargeting = False
        self._hash = None
        self._image_hash = None
        self.cost = 0
        self.accountId = ''
        self.RetargetingID = ''
        self.Recommended = ''

    @property
    def hash(self):
        if self._hash:
            return self._hash
        offerHash = {}
        offerHash['guid'] = self.id
        offerHash['guid_int'] = long(self.id_int)
        offerHash['title'] = self._trim_by_words(self.title, 35)
        offerHash['description'] = self._trim_by_words(self.description, 70)
        offerHash['url'] = self.url
        offerHash['campaignId'] = self.campaign
        offerHash['campaignId_int'] = long(self.campaign_int)
        offerHash['price'] = self.price
        offerHash['retargeting'] = self.retargeting
        offerHash['RetargetingID'] = self.RetargetingID
        offerHash['Recommended'] = self.Recommended
        self._hash = str(hashlib.md5(str(offerHash)).hexdigest())
        return self._hash

    @property
    def image_hash(self):
        if self._image_hash:
            return self._image_hash
        imageHash = {}
        imageHash['guid'] = self.id
        imageHash['guid_int'] = long(self.id_int)
        imageHash['campaignId'] = self.campaign
        imageHash['campaignId_int'] = long(self.campaign_int)
        imageHash['image'] = self.image
        imageHash['logo'] = self.logo
        self._image_hash = str(hashlib.md5(str(imageHash)).hexdigest())
        return self._image_hash

    def save(self, without_ratings=None):
        'Сохраняет предложение в базу данных'
        ctr = 0.25 * 100000
        rating = round((ctr * self.cost), 4)
        data = {'title': self._trim_by_words(self.title, 35),
                'price': self.price,
                'url': self.url,
                'image': '',
                'description': self._trim_by_words(self.description, 70),
                'campaignId': self.campaign,
                'campaignId_int': long(self.campaign_int),
                'campaignTitle': self.campaignTitle,
                'retargeting': self.retargeting,
                'rating': rating,
                'full_rating': rating,
                'hash': self.hash,
                'image_hash': self.image_hash,
                'cost': self.cost,
                'accountId': self.accountId,
                'RetargetingID': self.RetargetingID,
                'Recommended': self.Recommended
                }
        if without_ratings:
            del data['rating']
            del data['full_rating']
        return pymongo.UpdateOne({'guid': self.id, 'guid_int': long(self.id_int)},
                                 {'$set': data},
                                 upsert=True)

    def _trim_by_words(self, str, max_len):
        ''' Обрезает строку ``str`` до длины не более ``max_len`` с учётом слов '''
        if len(str) <= max_len:
            return str
        trimmed_simple = str[:max_len]
        trimmed_by_words = trimmed_simple.rpartition(' ')[0]
        return u'%s…' % (trimmed_by_words or trimmed_simple)
