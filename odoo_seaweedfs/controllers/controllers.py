# -*- coding: utf-8 -*-
from odoo import http

# class BaseFile(http.Controller):
#     @http.route('/base_file/base_file/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/base_file/base_file/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('base_file.listing', {
#             'root': '/base_file/base_file',
#             'objects': http.request.env['base_file.base_file'].search([]),
#         })

#     @http.route('/base_file/base_file/objects/<model("base_file.base_file"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('base_file.object', {
#             'object': obj
#         })