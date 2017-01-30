# encoding: utf-8
import cgi

from getmyad.lib.base import BaseController, render
from paste.urlparser import PkgResourcesParser
from pylons.middleware import error_document_template
from webhelpers.html.builder import literal
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import redirect, abort


class ErrorController(BaseController):
    """Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.

    """

    def document(self):
        """Render the error document"""
        request = self._py_object.request
        res = request.environ.get('pylons.original_response')
        code = cgi.escape(request.GET.get('code', str(res.status_int)))
        if code == "404":
            c.error_message = u'<h2>Запрашиваемая страница не найдена.</h2>'
        else:
            c.error_message = u'<h2>На данный момент сервис не доступен.</h2>\
                                <p>Проводяться технические работы по обновлению сервиса.</p>\
                                <p>Попробуйте зайти через пару минуту.</p>\
                                <p>Приносим свои извенения за временные неудобства.</p>\
                                <p>С уважением, поддержка Yottos.</p>'
        return render('/index.mako.html')

    def img(self, id):
        """Serve Pylons' stock images"""
        return self._serve_file('/'.join(['media/img', id]))

    def style(self, id):
        """Serve Pylons' stock stylesheets"""
        return self._serve_file('/'.join(['media/style', id]))

    def _serve_file(self, path):
        """Call Paste's FileApp (a WSGI application) to serve the file
        at the specified path
        """
        request = self._py_object.request
        request.environ['PATH_INFO'] = '/%s' % path
        return PkgResourcesParser('pylons', 'pylons')(request.environ, self.start_response)
