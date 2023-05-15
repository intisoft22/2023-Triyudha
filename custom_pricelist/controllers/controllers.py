# -*- coding: utf-8 -*-
# from odoo import http


# class CustomPricelist(http.Controller):
#     @http.route('/custom_pricelist/custom_pricelist/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_pricelist/custom_pricelist/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_pricelist.listing', {
#             'root': '/custom_pricelist/custom_pricelist',
#             'objects': http.request.env['custom_pricelist.custom_pricelist'].search([]),
#         })

#     @http.route('/custom_pricelist/custom_pricelist/objects/<model("custom_pricelist.custom_pricelist"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_pricelist.object', {
#             'object': obj
#         })
