# -*- coding: utf-8 -*-
from openerp import http

class lpeopenacademy(http.Controller):
    @http.route('/lpeopenacademy/lpeopenacademy/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/lpeopenacademy/lpeopenacademy/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('lpeopenacademy.listing', {
            'root': '/lpeopenacademy/lpeopenacademy',
            'objects': http.request.env['lpeopenacademy.course'].search([]),
        })

    @http.route('/lpeopenacademy/lpeopenacademy/objects/<model("lpeopenacademy.course"):obj>/', auth='public')
    def object(self, obj, **kw):
        return http.request.render('lpeopenacademy.object', {
            'object': obj
        })