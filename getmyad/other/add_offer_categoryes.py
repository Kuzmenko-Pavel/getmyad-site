#!/usr/bin/python
# This Python file uses the following encoding: utf-8
from uuid import uuid1

from pymongo import Connection


def  add_categories():
    main_db_host = 'yottos.ru,213.186.121.76:27018,213.186.121.199:27018'
    conn = Connection(host=main_db_host)
    db = conn.getmyad_db
    category = ['Финансы','Электроника','Аксессуары','Игры','Одежда','Дети','Техника','Медицина','Спорт','Посуда','Обучение','Зоотовары','Автомобили','Недвижимость','Стройка  и ремонт','Туризм','Красота','Книги','Еда']
    for item in category:
        guid = str(uuid1()).lower()
        db.offer.categories.insert({'guid': guid,
                                    'name': item},
                                    safe=True)

if __name__ == '__main__':
    #add_categories()
