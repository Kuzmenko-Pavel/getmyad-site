# -*- coding: utf-8 -*-
# This Python file uses the following encoding: utf-8
"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password

from routes import url_for
from webhelpers.html.tags import *
from datetime import datetime
from pylons.controllers.util import redirect
import json
import bson.json_util



class progressBar:
    def __init__(self, minValue = 0, maxValue = 10, totalWidth=12):
        self.progBar = "[]"   # This holds the progress bar string
        self.min = minValue
        self.max = maxValue
        self.span = maxValue - minValue
        self.width = totalWidth
        self.amount = 0       # When amount == max, we are 100% done 
        self.updateAmount(0)  # Build progress bar string

    def updateAmount(self, newAmount = 0):
        if newAmount < self.min: newAmount = self.min
        if newAmount > self.max: newAmount = self.max
        self.amount = newAmount

        # Figure out the new percent done, round to an integer
        diffFromMin = float(self.amount - self.min)
        percentDone = (diffFromMin / float(self.span)) * 100.0
        percentDone = round(percentDone)
        percentDone = int(percentDone)

        # Figure out how many hash bars the percentage should be
        allFull = self.width - 2
        numHashes = (percentDone / 100.0) * allFull
        numHashes = int(round(numHashes))

        # build a progress bar with hashes and spaces
        self.progBar = "[" + '#'*numHashes + ' '*(allFull-numHashes) + "]"

        # figure out where to put the percentage, roughly centered
        percentPlace = (len(self.progBar) / 2) - len(str(percentDone)) 
        percentString = str(percentDone) + "%"

        # slice the percentage into the bar
        self.progBar = self.progBar[0:percentPlace] + percentString + \
                       self.progBar[percentPlace+len(percentString):]

    def __str__(self):
        return str(self.progBar)



def dateFromStr(str):
    """Возвращает объект datetime из строки вида 'чч.мм.гггг' """
    try:
        day = int(str[0:2])
        month = int(str[3:5])
        year = int(str[6:10])
        return datetime(year, month, day)
    except:
        return None


def datetimeFromStr(str):
    """Возвращает объект datetime из строки вида 'чч.мм.гггг ЧЧ:ММ' """
    try:
        day = int(str[0:2])
        month = int(str[3:5])
        year = int(str[6:10])
        hour = int(str[11:13])
        minute = int(str[14:16])
        return datetime(year, month, day, hour, minute)
    except:
        return None

def trim_time(datetime_object):
    ''' Возвращает объект datetime.datetime с обнулённым временем '''
    return datetime(datetime_object.year,
                    datetime_object.month,
                    datetime_object.day)

def userNotAuthorizedError():
    return JSON({'error': True, 'error_type': 'authorizedError',
                 'msg': u"Пожалуйста, войдите в систему GetMyAd", 'ok': False}) 

def insufficientRightsError():
    return JSON({'error': True,
                 'msg': u"Недостаточно прав для осуществления операции",
                 'ok': False}) 


def jgridDataWrapper(data, userdata=None, page=None, records_on_page=None, count=None, total_pages=None,
                     json=True):
    """ Принимает список значений колонок и возвращает json для таблиц jqGrid.
        Строит пейджинг по массиву данных или передает параметры пейджинга передаваемые
        ему на вход (при условии организации пейджинга с учётом выборки с бд)
        Для организации пейджинга из массива данных можно передать параметры ``page`` -- номер
        текущей страницы, ``records_on_page`` -- количество записей на одной
        странице.
        Для организации пейджинга при условии организации с учётом выборки с бд можно передать параметры
        ``page`` -- номер текущей страницы, ``count``- колво записей, ``total_pages`` - колво страниц.
    """
    if count is None and total_pages is None:
        records = len(data)
        if page is not None and records_on_page is not None:
            try:
                page = int(page)
            except ValueError:
                page = 1

            try:
                records_on_page = int(records_on_page)
            except ValueError:
                records_on_page = 20

            if page == 0:
                page = 1
            start_record = (page - 1) * records_on_page
            end_record = page * records_on_page
            total_pages = (records-1) / records_on_page + 1
            data = data[start_record:end_record]
            records = len(data)
        else:
            if records:
                total_pages = page = 1
            else:
                total_pages = page = 0
    else:
        records = int(count)
        try:
            total_pages = int(total_pages)
        except ValueError:
            total_pages = 1
        try:
            page = int(page)
        except ValueError:
            page = 1
        
    output = {'total': total_pages,
               'page': page,
               'records': records,
               'rows': [{'cell': x, 'id': index + 1}
                        for index,x in enumerate(data)]
               }
    if userdata:
        output['userdata'] = userdata
    return JSON(output) if json else output

def jqGridLocalData(data, columns_list):
    """ Принимает таблицу ``data`` (list of tupples) и список id колонок
        jqGrid ``columns_list``.

        Возвращает JSON, который можно установить как источник данных
        при datatype: 'local'
    """
    output = []
    for row in data:
        output.append(dict(
                          zip(columns_list, row)))
    return JSON(output)


def formatMoney(value):
    """ Форматирует денежную величину """
    return u'%.2f грн' % value

def JSON(obj):
    """Возвращает JSON-представление объекта obj"""
    return json.dumps(obj, default=bson.json_util.default, ensure_ascii=True)

def avg(collection):
    ''' Возвращает среднее значение коллекции '''
    if not collection:
        return 0
    return sum(collection) / len(collection)
def year():
    dt = datetime.now()
    return dt.strftime('%Y')
   
def secontToString(seconds, format):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    data = {'h':int(h), 'm':int(m), 's':int(s)}
    return format.format(**data)
