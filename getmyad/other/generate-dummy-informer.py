#!/usr/bin/python
# encoding: utf-8
from ftplib import FTP
import StringIO
import random

import pymongo

social_ads = [{'title': u'YOTTOS за креатив!',
               'description': u'Разрабатываем привлекательные информеры! Без плагиата!',
               'url': u'https://yottos.com/',
               'image': u'https://cdnt.yottos.com/getmyad/img/6b18beeca61c11e4923e002590d97638.png'
               },
               {'title': u'Делая хорошую рекламу...',
                'description': u'Мы развиваем Ваш бизнес и улучшаем качество жизни покупателей.',
                'url': u'https://yottos.com/',
                'image': u'https://cdnt.yottos.com/getmyad/img/e9cdba0a85cc11e48104002590d590d0.png'
                },
                {'title': u'YOTTOS — команда профессионалов',
                 'description': u'Стараемся для Вашего успеха!',
                 'url': u'https://yottos.com/',
                 'image': u'https://cdnt.yottos.com/getmyad/img/6af67c60a61c11e4923e002590d97638.png'
                },
                {'title': u'Успех — не просто удача',
                 'description': u'Это упорная работа и возможность, которую вы готовы ухватить!',
                 'url': u'https://yottos.com/',
                 'image': u'https://cdnt.yottos.com/getmyad/img/eaf47c9885cc11e48104002590d590d0.png'
                 },
                {'title': u'Реклама на русскоязычных сайтах',
                 'description': u'Реклама YOTTOS -  Ваше конкурентное преимущество.',
                 'url': u'https://yottos.com/',
                 'image': u'https://cdnt.yottos.com/getmyad/img/ea3ab81c85cc11e48104002590d590d0.png'
                 },
                {'title': u'Креативная реклама YOTTOS',
                 'description': u'Реклама на русскоязычных сайтах, забота о развитии Вашего бизнеса!',
                 'url': u'https://yottos.com/',
                 'image': u'https://cdnt.yottos.com/getmyad/img/6b3fd748a61c11e4923e002590d97638.png'
                 },
                {'title': u'Реклама на русскоязычных сайтах',
                 'description': u'YOTTOS - создаем эффективную рекламу Вашего бизнеса!',
                 'url': u'https://yottos.com/',
                 'image': u'https://cdnt.yottos.com/getmyad/img/6a96a4e8a61c11e4923e002590d97638.png'
                 },
                 {'title': u'Делая хорошую рекламу...',
                  'description': u'Мы развиваем Ваш бизнес и улучшаем качество жизни покупателей.',
                  'url': u'https://yottos.com/',
                  'image': u'https://cdnt.yottos.com/getmyad/img/6adcf9c0a61c11e4923e002590d97638.png'
                  }
              ]

def _generate_social_ads(inf):
    ''' Возвращает HTML-код заглушки с социальной рекламой,
        которая будет показана при падении сервиса
    '''
    try:
        items_count = int(inf['admaker']['Main']['itemsNumber'])
    except:
        items_count = 0
    offers = ''
    try:
        if len(social_ads) >= items_count:
            tmp_list = random.sample(social_ads, items_count)
        else:
            if (len(social_ads) % items_count) * len(social_ads) > items_count:
                tmp_list = random.sample((len(social_ads) % items_count) * social_ads, items_count)
            else:
                tmp_list = random.sample(items_count * social_ads, items_count)

    except Exception as e:
        print e, len(social_ads), items_count, (len(social_ads) % items_count)
        raise

    for i in xrange(0, items_count):
        try:
            adv = tmp_list[i % len(tmp_list)]

            offers += ('''<div class="advBlock"><a class="advHeader" href="%(url)s" target="_blank">''' +
                       '''%(title)s</a><a class="advDescription" href="%(url)s" target="_blank">''' +
                       '''%(description)s</a><a class="advCost" href="%(url)s" target="_blank"></a>''' +
                       '''<a href="%(url)s" target="_blank"><img class="advImage" src="%(img)s" alt="%(title)s"/></a></div>'''
                       ) % {'url': adv['url'], 'title': adv['title'], 'description': adv['description'], 'img': adv['image']}
        except Exception as e:
            print e , len(tmp_list), i % len(tmp_list)
            raise
    return '''
<html><head><META http-equiv="Content-Type" content="text/html; charset=utf-8"><meta name="robots" content="nofollow" /><style type="text/css">html, body { padding: 0; margin: 0; border: 0; }</style><!--[if lte IE 6]><script type="text/javascript" src="//cdn.yottos.com/getmyad/supersleight-min.js"></script><![endif]-->
%(css)s
</head>
<body>
<div id='mainContainer'><div id="ads" style="position: absolute; left:0; top: 0">
%(offers)s
</div><div id='adInfo'><a href="//yottos.com.ua" target="_blank"></a></div>
</body>
</html>''' % {'css': inf.get('css'), 'offers': offers}

def upload_all():
    # Параметры FTP для заливки загрузчиков информеров
    informer_loader_ftp = 'srv-3.yottos.com'
    informer_loader_ftp_user = 'stc'
    informer_loader_ftp_password = '$www-app$'
    informer_loader_ftp_path = ''
    db = pymongo.Connection(host='srv-2.yottos.com:27018,srv-9.yottos.com:27018,srv-1.yottos.com:27017,srv-8.yottos.com:27018,srv-3.yottos.com:27018').getmyad_db
    
    informers = db.informer.find().sort("lastModified", -1)
    
    for informer in informers:
        guid = informer.get('guid')
        ftp = FTP(host=informer_loader_ftp,
                  user=informer_loader_ftp_user,
                  passwd=informer_loader_ftp_password)
        ftp.cwd(informer_loader_ftp_path)
        loader = StringIO.StringIO()
        loader.write(_generate_social_ads(informer).encode('utf-8'))
        loader.seek(0)
        print "Uploading %s" % guid
        ftp.storlines('STOR emergency-%s.html' % guid, loader)
        ftp.quit()
        loader.close()
        ftp = FTP(host=informer_loader_ftp,
                  user=informer_loader_ftp_user,
                  passwd=informer_loader_ftp_password)
        ftp.cwd(informer_loader_ftp_path)
        loader = StringIO.StringIO()
        loader.write(_generate_social_ads(informer).encode('utf-8'))
        loader.seek(0)
        print "Uploading %s" % guid.upper()
        ftp.storlines('STOR emergency-%s.html' % guid.upper(), loader)
        ftp.quit()
        loader.close()
    
    

if __name__ == '__main__':
    upload_all()
    print "Finished!"
    exit()
    
