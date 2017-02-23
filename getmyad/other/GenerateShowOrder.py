# -*- coding: utf-8 -*-
# Этот скрипт устарел и в данный момент не используется
# Оставлен на всякий случай (может содержать полезные куски кода)

from optparse import OptionParser

from pymongo import Connection
import pyodbc

conn = Connection()
mongo = conn.getmyadTemporaryDisabled_db
#connection_string = 'DRIVER={SQL Server};server=WS1;DATABASE=1gb_YottosAdload;UID=sa;PWD=1'
connection_string = 'DRIVER={SQL Server};server=213.186.119.106;DATABASE=1gb_YottosGetMyAd;UID=web;PWD=odif8duuisdofj'

mssql = pyodbc.connect(connection_string, autocommit=True)


def create_ranges(data):
    """
        Разбивает диапазон (0..1) на поддиапазоны в соответствии с показателем (rate) каждого объекта. 

        data       [(A, rate1), (B, rate2), ...]
        Возвращает [(A, left_bound, right_bound), (B, left_bound, right_bound), ...]
    """ 
    S = sum( [x[1] for x in data] )
    left_bound = 0
    result = []
    for x in data:
        right_bound = left_bound + float(x[1]) / S 
        result.append( (x[0], left_bound, right_bound) )
        left_bound = right_bound
    return result


def lots_ctr(advertise_id, informer_id):
    """Возвращает CTR товаров, входящих в выгрузку advertise_id по рекламной выгрузке informer_id"""
    cursor = mssql.cursor()
    cursor.execute('''select distinct LotID from Lots where Active=1 and AdvertiseID=?''', advertise_id)
    lots = [x[0] for x in cursor]
    
    # Получаем ctr товаров, по которым уже есть какая-то статистика
    lots_stats = mongo.stats_daily.group(key = ['lot.guid'],
                                        condition = {'adv': informer_id, 'lot.guid': {'$in': lots}},
                                        initial = {'clicks': 0, 'impressions': 0},
                                        reduce = '''
                                            function (object, previous) {
                                                previous.clicks += isNaN(object.clicks)? 0 : object.clicks;
                                                previous.impressions += isNaN(object.impressions)? 0: object.impressions;
                                            }
                                        ''',
                                        finalize = '''
                                            function (object) {
                                                if (object.impressions)
                                                    object.ctr = object.clicks / object.impressions;
                                                else
                                                    object.ctr = 0;
                                            }
                                        ''')
    # Составляем словарь {Lot: {clicks: 0, impressions: 0, ctr: 0}}
    ctr = dict([(x['lot.guid'], {'clicks': x['clicks'], 'impressions': x['impressions'],'ctr': x['ctr']}) for x in lots_stats])
    # Добавляем товары, по которым ещё нет статистики
    for lot in lots:
        if not lot in ctr:
            ctr[lot] = {'clicks': 0, 'impressions': 0, 'ctr': 0}
    return [{'lot.guid': x,
             'clicks': ctr[x]['clicks'],
             'impressions': ctr[x]['impressions'],
             'ctr': ctr[x]['ctr']} for x in ctr.keys()]



def advertise_ctr(advertise_id, informer_id):
    """Возвращает CTR рекламной выгрузки advertise_id по рекламной выгрузке informer_id"""
    try:
        data = lots_ctr(advertise_id, informer_id)
        return float(sum([x['clicks'] for x in data])) / sum(x['impressions'] for x in data)
    except:
        return 0
         

def advertises_rates(informer_id):
    """Возвращает рейтинги рекламных кампаний для выгрузки informer_id
    Рейтинг определяется как CTR * цена_за_клик.
    """
    def avg(list):
        return (sum(list) / len(list)) if len(list) else 0
    
    # Смотрим, есть ли "эксклюзивные кампании для площадки". Если есть, то показываем только их
    cursor = mssql.cursor()
    cursor.execute('''SELECT  AdvertiseID, ClickCost, Title from Advertise
                      WHERE   [Enabled] = 1 and
                              TemporaryDisabled <> 1 and
                              AdvertiseID in (select AdvertiseID from AdvertiseExclusive where ScriptID=?)''',
                      informer_id)
    advertises = [{'advertise' : x[0], 'click_cost': x[1]} for x in cursor]
    if not advertises:
        # Выбираем все кампании, кроме помеченных как игнорируемые данной рекламной площадки
        cursor.execute('''SELECT  AdvertiseID, ClickCost, Title from Advertise
                          WHERE   [Enabled]=1 and
                                  TemporaryDisabled <> 1 and
                                  Common=1 and
                                  AdvertiseID not in (select AdvertiseID from AdvertiseIgnored where ScriptID=?)''',
                          informer_id)
        advertises = [{'advertise' : x[0], 'click_cost': x[1]} for x in cursor]
    
    # Получаем CTR рекламных кампаний
    for x in advertises:
        x['CTR'] = advertise_ctr(x['advertise'], informer_id)
    
    # Считаем рейтинг
    mid_CTR = avg([x['CTR'] for x in advertises if x['CTR']]) or 1
    mid_click_cost = avg([x['click_cost'] for x in advertises if x['click_cost']]) or 1

    for x in advertises:
        ctr = x['CTR'] or mid_CTR
        click_cost = x['click_cost'] or mid_click_cost
        x['rate'] = float(ctr) #* float(click_cost)        # Временно не учитываем цену за клик



    return advertises   


def informers_list():
    """Возвращает список рекламных выгрузок"""
    cursor = mssql.cursor()
    cursor.execute('select ScriptID from Scripts')
    return [x[0] for x in cursor] 


def save():
    """Сохраняет просчитанные данные в mongo"""
    cursor = mssql.cursor()
    cursor.execute('select AdvertiseID from Advertise where [Enabled] = 1 and TemporaryDisabled<>1')
    advertises = [x[0] for x in cursor]
    informers = informers_list()

    # Сохраняем рейтинги рекламных кампаний
    for informer in informers:
        print "Processing campaigns, informer #", informer 
        rates = [{'advertise': x['advertise'], 'rate': x['rate']} for x in advertises_rates(informer)]
        # Нормализуем рейтинги
        summ = sum([x['rate'] for x in rates])
        for r in rates:
            r['rate'] =  r['rate'] / summ
        
        mongo['rates.advertise'].update({'informer' : informer},
                                        {'$set': {'rates': rates}},
                                        upsert=True)

    # Сохраняем данные по товарам
    for informer in informers:
        print "Processing lots, informer #", informer
        for advertise in advertises:
            rates = [{'lot': x['lot.guid'], 'ctr': x['ctr']} for x in lots_ctr(advertise, informer)]
            summ = sum(x['ctr'] for x in rates) or 1
            count = len([x['ctr'] for x in rates])
            if not count:
                count = 1 #break
            avg = float(summ) / count
            for x in rates:
                if not x['ctr']:
                    x['ctr'] = avg
            summ = sum(x['ctr'] for x in rates) or 1            
            for x in rates:
                x['rate'] = x['ctr'] / summ

            mongo['rates.lot'].update({'informer': informer, 'advertise': advertise},
                                      {'$set': {'rates': rates}},
                                      upsert=True)


def startAdvertise(advertise):
    """Запускает объявления по расписанию"""
    cursor = mssql.cursor()
    cursor.execute("update Advertise set TemporaryDisabled=0 where AdvertiseID=?", advertise)
    cursor.execute("exec dbo.s_restart_advertise ?", advertise)
    save()


def stopAdvertise(advertise):
    """Остановка объявлений по расписанию"""
    cursor = mssql.cursor()
    cursor.execute("update Advertise set TemporaryDisabled=1 where AdvertiseID=?", advertise)
    cursor.execute("exec dbo.s_restart_advertise ?", advertise)
    save()


def generate():
    cursor = mssql.cursor()        
    cursor.execute("exec dbo.s_restart_all_advertises")
    save()


def usage():
    print """Generates GetMyAd ratings, start/stop markets"""


def main():    
    parser = OptionParser(usage=usage())
    parser.add_option("-g", "--generate", help="Generate all ratings", action="store_true", default=False, dest="generate")
    parser.add_option("-s", "--start", help="starts selected advertise", action="store_true", default=False, dest="start")
    parser.add_option("-S", "--stop", help="stops selected advertise", action="store_true", default=False, dest="stop")
    parser.add_option("-a", "--advertise", help="advertise guid to operate on", dest="advertise")
    (options, args) = parser.parse_args()
    if options.generate:
        generate()
    if options.start and options.advertise:
        startAdvertise(options.advertise)
    if options.stop and options.advertise:
        stopAdvertise(options.advertise)
    
    
if __name__ == "__main__":
    main()