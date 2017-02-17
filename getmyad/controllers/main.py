# -*- coding: utf-8 -*-
from datetime import datetime
from getmyad.lib.base import BaseController, render
from pylons import request, session, tmpl_context as c, url,  app_globals
from pylons.controllers.util import redirect
import logging

log = logging.getLogger(__name__)

class MainController(BaseController):

    def index(self):
        c.Comment=True
        if session.get('user'):
            if not session.get('isManager', False):
                return redirect(url(controller='private', action='index'))
            else:
                return redirect(url(controller='manager', action='index'))
        
        errorMessage = session.get('error_message')
        if errorMessage:
            session.delete()
        return render('/index.mako.html', extra_vars = 
                      {'errorMessage': errorMessage})

    def signIn(self):
        """Вход пользователя. Должны передаваться параметры login и password"""
        c.Comment=False 
        login = request.POST.get("login")
        password = request.POST.get('password')
        user = app_globals.db.users.find_one({'login': login,
                                              'password': password})
        if user <> None:
            blocked = user.get('blocked', False)
            if blocked == 'banned':
                session['error_message'] = u'Аккаунт заблокирован'
                session.save()
                return redirect(url(controller="main", action="index"))
            if blocked == 'light':
                c.login = login
                return render('/user/account_blocked.mako.html')
            
            session['user'] = user['login']
            session['isManager'] = user.get('manager', False)
            session.save()
            if not session['isManager']:
                return redirect(url(controller="private", action="index"))
            else:
                return redirect(url(controller="manager", action="index"))
        else:
            session['error_message'] = u'Неверный логин или пароль!'
            session.save()
            return redirect(url(controller="main", action="index"))


    def signOut(self):
        """Выход пользователя"""
        c.Comment=False 
        # записываем в бд время выхода из аккаунта
        app_globals.db.users.update({'login' : session.get('user')}, {'$set': {'signOutTime': datetime.today()}})
        if 'user' in session:
            del session['user']
        if 'adload_user' in session:
            del session['adload_user']
        session.delete()
        return redirect(url(controller="main", action="index"))

    

    def search(self):
        """Поиск в Yottos"""
        query = request.params.get('QueryText') 
        if query:
            return redirect(url("http://yottos.ru/Result.aspx", q=query))
        else:
            return redirect("http://yottos.ru")
        

    def resumeAccount(self, id):
        ''' Возобновление временно заблокированного аккаунта GetMyAd '''
        user = app_globals.db.users.find_one({'login' : id})
        if user.get('blocked') == 'light':
            user['blocked'] = False
            app_globals.db.users.save(user)
        return redirect(url(controller="main", action="index"))
