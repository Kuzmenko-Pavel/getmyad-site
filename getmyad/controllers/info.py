# -*- coding: utf-8 -*-
import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from getmyad.lib.base import BaseController, render

log = logging.getLogger(__name__)

class InfoController(BaseController):

    def index(self):
        c.Comment=True        
        return self.terms_and_conditions()
    
    def faq(self):
        """Часто задаваемые вопросы"""
        c.initial_href = "#faq"
        return render('/faq.mako.html')
    
    def increase(self):
        """Часто задаваемые вопросы"""
        c.initial_href = "#increase"
        return render('/faq.mako.html')
    
    def answers(self):
        """Часто задаваемые вопросы"""
        return render('/faq.mako.html')
    
    def terms_and_conditions(self):
        """Общие условия программы GetMyAd"""
        c.Comment=False 
        return render('/terms-and-conditions.mako.html')
    
    def rules(self):
        """Правила программы GetMyAd"""
        c.Comment=False 
        return render('/rules.mako.html')
    
    def growing(self):
        """Рост доходности"""
        c.Comment=False 
        return render("/growing.mako.html")
    
