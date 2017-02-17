#!/usr/bin/python
# encoding: utf-8
import pymongo
import re
def size_all():
    db = pymongo.Connection(host='yottos.com').getmyad_db
    informers = [x['guid'] for x in db.informer.find({}, ['guid'])]
    informers += map(lambda x: x.upper(), informers)        # Для тех, кому выдавался upper-case GUID
    for informer in informers:
        adv = db.informer.find_one({'guid': informer.lower()})
        if not adv:
            print "None"
        try:
            width = int(re.match('[0-9]+', adv['admaker']['Main']['width']).group(0))
            height = int(re.match('[0-9]+', adv['admaker']['Main']['height']).group(0)) 
        except:
            raise Exception("Incorrect size dimensions for informer %s" % informer)
        try:
            border = int(re.match('[0-9]+', adv['admaker']['Main']['borderWidth']).group(0))
        except:
            border = 1
        width += border * 2
        height += border * 2
        adv['width'] = width
        adv['height'] = height
        db.informer.save(adv)
        
if __name__ == '__main__':
#    size_all()
