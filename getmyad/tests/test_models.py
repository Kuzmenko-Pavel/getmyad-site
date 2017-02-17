# This Python file uses the following encoding: utf-8
from getmyad.model import Account, Permission
from getmyad import model
from pymongo import Connection



class TestAccount:
    
    def setUp(self):
        self.mongo = Connection()
        self.mongo.drop_database('getmyad_tests')
        self.db = self.mongo['getmyad_tests']
        model.Options.db = self.db
    
    def tearDown(self):
        self.mongo.disconnect()

    def test_register_and_load_account(self):
        ''' Регистрация и загрузка аккаунтов '''
        acc1 = Account(login='test')
        acc1.email = 'silver@ukr.net'
        acc1.manager_get = 'manager'
        acc1.min_out_sum = 30
        acc1.owner_name = u'Вася Пупкин'
        acc1.password = '123qwe'
        acc1.phone = '+38(050) 123-123-12'
        acc1.register()

        acc2 = Account(login='test')
        acc2.load()

        assert acc1.email == acc2.email == 'silver@ukr.net'
        assert acc1.manager_get == acc2.manager_get == 'manager'
        assert acc1.min_out_sum == acc2.min_out_sum == 30
        assert acc1.owner_name == acc2.owner_name == u'Вася Пупкин'
        assert acc1.password == acc2.password == '123qwe'
        assert acc1.phone == acc2.phone == '+38(050) 123-123-12'
        assert acc1.account_type == Account.User
        
        assert acc1.exists(), 'Проверка на существование не работает для зарегистрированных аккаунтов'
        assert not Account(login='blablabla').exists(), 'Проверка на существование не работает для не существующих аккаунтов'

    def test_register_account_duplicate(self):
        ''' Повторная регистрация '''
        try:
            acc = Account('test_login')
            acc.register()
            acc.register()
            raise AssertionError('Duplicate logins are not allowed')
        except Account.AlreadyExistsError:
            pass
        except:
            raise
    
    def test_register_account_invalid_chars(self):
        ''' Регистрация аккаунтов с недопустимыми символами '''
        acc1 = Account('login_ends_with_space ')
        acc1.register()

        acc2 = Account(login = 'login_ends_with_space')
        try:
            acc2.load()
        except Account.NotFoundError:
            raise AssertionError('Space at the end of login wasn\'t trimmed')
        
    def test_account_lazy_load(self):
        ''' Ленивая загрузка аккаунтов '''
        acc0 = Account('test_login')
        acc0.account_type = Account.Manager
        acc0.register()
        
        acc1 = Account('test_login')
        assert acc1.account_type == acc0.account_type == Account.Manager, \
            'Аккаунт автоматически не загружается при запросе свойства account_type'
        

    def test_account_domains(self):
        ''' Домены пользователя '''
        acc = Account('test_login')
        acc.register()
        assert len(acc.domains.list()) == 0
        
        acc.domains.add('http://yottos.com')
        acc.domains.add('http://www.yottos.com.ua')
        acc.domains.add('yottos.ru')
        domains = acc.domains.list()
        assert len(domains) == 3 and \
                'yottos.com' in domains and \
                'yottos.com.ua' in domains and \
                'yottos.ru' in domains, \
                'Не работает добавление доменов domains, или не обрезается "http://"'
        
        acc2 = Account('test_login')
        acc2.load()         
        domains = acc2.domains.list()
        assert len(domains) == 3 and \
                'yottos.com' in domains and \
                'yottos.com.ua' in domains and \
                'yottos.ru' in domains, \
                'domains not loaded'
        
        acc3 = Account('test_login2')
        acc3.register()
        acc3.domains.add('http://first.com')
        acc3.domains.add('http://duplicate.com')
        acc3.domains.add('www.duplicate.com')
        domains = acc3.domains.list()
        assert len(domains) == 2, "Duplicate domains shouldn't be added"
        
    def test_account_domains_requests(self):
        ''' Заявки на регистрацию домена '''
        acc1 = Account('test_login1')
        acc1.register()
        assert not acc1.domains.list(), 'У новых акканунтов не должно быть одобренных доменов'
        assert not acc1.domains.list_requests(), 'У новых аккаунтов не должно быть заявок на регистрацию домена'
        acc1.domains.add_request('http://yottos.com')
        acc1.domains.add_request('http://yottos.com.ua')
        assert len(acc1.domains.list_requests()) == 2, 'Не работает добавление заявок на регистрацию домена'
        assert not acc1.domains.list(), 'Добавление заявок на регистрацию домена влияет на одобренные домены'
        acc1.domains.approve_request('http://yottos.com')
        assert len(acc1.domains.list()) == 1 and \
               'yottos.com' in acc1.domains.list(), \
               'Одобренные заявки не сохраняются'
        assert len(acc1.domains.list_requests()) == 1 and \
               'yottos.com' not in acc1.domains.list_requests(), \
               'Заявки на регистрацию домена не убираются при одобрении'
        
    def test_permissions(self):
        ''' Права (разрешения) пользователей '''
        manager = Account('manager')
        manager.account_type = Account.Manager
        manager.register()
        manager = Account('manager')
        manager.load()
        admin = Account('root')
        admin.account_type = Account.Administrator
        admin.register()
        admin.load()
        assert manager.account_type == Account.Manager, 'Не сохранился тип регистрируемого аккаунта'
        assert admin.account_type == Account.Administrator, 'Не сохранился тип регистрируемого аккаунта'
        assert Permission(manager).has(Permission.VIEW_ALL_USERS_STATS) == False, \
                    "По умолчанию должен создаваться менеджер с минимальными правами"
        assert Permission(admin).has(Permission.VIEW_ALL_USERS_STATS) == True and \
               Permission(admin).has(Permission.USER_DOMAINS_MODERATION) == True, \
                    "У администратора должны быть все права"
        
        try:
            Permission(manager).grant_to(manager, Permission.VIEW_ALL_USERS_STATS)
        except Permission.InsufficientRightsError:
            pass
        else:
            raise AssertionError('Нельзя передавать права от имени аккаунта, который не обладает этими правами')
            
        Permission(admin).grant_to(manager, Permission.VIEW_ALL_USERS_STATS)
        assert Permission(manager).has(Permission.VIEW_ALL_USERS_STATS), 'Разрешение от администратора не передалось'
        