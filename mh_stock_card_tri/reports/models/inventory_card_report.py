# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

from datetime import datetime, timedelta, date
from pytz import timezone
import time


from lxml import etree

import json

class InventoryCardReportWizard(models.TransientModel):
    _name = 'inventory.card.report.wizard'


    tglawal = fields.Date('Start Date', default=date.today(), required=True)
    tglakhir = fields.Date('End Date', default=date.today(), required=True)


    location_id = fields.Many2one(
        'stock.location', 'Location',
        domain=[('usage', 'in', ['internal', 'transit'])],
        ondelete="cascade", required=True )

    categ_id = fields.Many2one('product.category', 'Category', required=True)
    product_ids = fields.Many2many(
        'product.product',
        'product_product_card_report_rel',
        'report_card_id',
        'product_id',
        'Product', required=True
    )

    def get_excel_report(self):
        # redirect ke controller /sale/excel_report untuk generate file excel
        return {
            'type': 'ir.actions.act_url',
            'url': '/inventory_card/excel_report/%s' % (self.id),
            'target': 'new',
        }

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        if self.categ_id:
            self.product_ids=False
            Product = self.env['product.product']
            categ_products = Product.search([('categ_id', 'child_of', self.categ_id.id)])
            # print(categ_products)
            # print("===============================")
            return {'domain': {'product_ids': [('id', 'in', categ_products.ids)]}}


    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form',
    #                     toolbar=False, submenu=False):
    #     res = super(InventoryCardReportWizard, self).fields_view_get(
    #         view_id=view_id, view_type=view_type,
    #         toolbar=toolbar, submenu=submenu)
    #
    #     users = self.env['res.users'].search(
    #         [('id', '=', self.env.uid)], limit=1)
    #     wh = []
    #     warehouseuser = []
    #     for u in users:
    #         for b in u.branch_ids:
    #             wh.append(str(b.id))
    #             locuser = self.env['stock.location'].search([('name', '=', b.code)])
    #
    #             locuser2 = self.env['stock.location'].search([('id', 'child_of', locuser[0].id)])
    #             for l in locuser2:
    #                 warehouseuser.append(str(l.id))
    #     location_ids = warehouseuser
    #     # print(location_ids)
    #     doc = etree.XML(res['arch'])
    #     for node in doc.xpath("//field[@name='location_id']"):
    #         if location_ids:
    #             domain= "[('id', 'in', [" + ', '.join(location_ids) + "]), ('usage', '=', 'internal')]"
    #             # print(domain)
    #             node.set('domain',domain)
    #             setup_modifiers(node, res['fields'][node.get('name', False)])
    #         # print(node)
    #     # print(doc)
    #     res['arch'] = etree.tostring(doc, encoding='unicode')
    #     return res

