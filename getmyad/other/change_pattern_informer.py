#!/usr/bin/python
# This Python file uses the following encoding: utf-8
from pymongo import Connection


def  change_pattern():
    main_db_host = 'yottos.ru,213.186.121.76:27018,213.186.121.199:27018'
    conn = Connection(host=main_db_host)
    db = conn.getmyad_db
    cur = db.informer.find({ "user": "aquariumist.kiev.ua" })
    for item in cur:
        print item['width'], item['width_banner'], item['height'], item['height_banner']
        pattern = db.informer.patterns.find_one({ "height": int(item['height']), "height_baner": int(item['height_banner']),\
                "width_baner": int(item['width_banner']), "width": int(item['width']) })
        print pattern['title']
        pattern['admaker'] = item['admaker']
        db.informer.patterns.save(pattern)


if __name__ == '__main__':
    #change_pattern()
