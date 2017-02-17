# -*- coding: utf-8 -*-
import logging
import datetime
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
import os
import StringIO
from getmyad.lib.base import BaseController, render
from getmyad.lib.capcha import Capcha
from getmyad.tasks.mail import registration_request_manager, registration_request_user

log = logging.getLogger(__name__)


class RegisterUserController(BaseController):
    ''' Регистрация пользователя '''
    
    def index(self):
        c.user_name = session.pop('user_name', '')
        c.user_url = session.pop('user_url', '')
        c.user_phone = session.pop('user_phone', '')
        c.user_email = session.pop('user_email', '')
        c.capcha_error = session.pop('capcha_error', '')
        session.save()
        return render('/register_user.mako.html')
    
    def capcha(self):
        ''' Возвращает изображение капчи '''
        c = Capcha()
        font_file = '../public/font/myfont.ttf'
        c.font_file = os.path.join(os.path.dirname(__file__), font_file)
        c.generate()
        
        session["register_capcha"] = c.text
        session.save()
        buffer = StringIO.StringIO()
        c.image.save(buffer, "PNG")
        
        response.content_type = "image/png"
        return buffer.getvalue()

    def send(self):
        res = request.params
        print "YES"
        if res.get('Capcha') != session.get("register_capcha"):
            session['user_name'] = res.get('UserNameText')
            session['user_url'] = res.get('SiteUrl')
            session['user_email'] = res.get('Email')
            session['user_phone'] = res.get('PhoneNumber')
            session['capcha_error'] = u'Неверно введены цифры с картинки. Попробуйте ещё раз.'
            session.save()
            return redirect(url(controller="register_user", action="index"))
            
        try:
            registration_request_manager.delay(user_name=res['UserNameText'], site_url=res['SiteUrl'], email=res['Email'], phone_number=res['PhoneNumber'], time=datetime.datetime.now().strftime("%d.%m.%y %H:%M"))
        except Exception as ex:
            registration_request_manager(user_name=res['UserNameText'], site_url=res['SiteUrl'], email=res['Email'], phone_number=res['PhoneNumber'], time=datetime.datetime.now().strftime("%d.%m.%y %H:%M"))
        try:
            registration_request_user.delay(email=res.get('Email'), user_name=res['UserNameText'], site_url=res['SiteUrl'])
        except Exception as ex:
            registration_request_user(email=res.get('Email'), user_name=res['UserNameText'], site_url=res['SiteUrl'])

        session['just_registered'] = True
        session.save()
        return redirect('/register_user/thanks')

         
    def thanks(self):
        if not session.get('just_registered'):
            return redirect('/')
        c.text_message = """
        """
        return render('/thanks_user.mako.html')
