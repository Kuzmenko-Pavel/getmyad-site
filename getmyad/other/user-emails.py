#!/usr/bin/python
# encoding: utf-8
# Печатает адреса электронной почты пользователей GetMyAd

import pymongo

conn = pymongo.Connection('yottos.com')
db = conn.getmyad_db
for user in db.users.find():
    if user.get('email') and user.get('ownerName'):
        print '"%s" <%s>,' % (user['ownerName'], user['email']), 
