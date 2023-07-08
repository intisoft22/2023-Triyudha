# -*- coding: utf-8 -*-
from odoo import api, fields, models
class SalesContractField(models.Model):
    _inherit = 'purchase.order.line'

    sales_contract = fields.Many2one('sales.contract', string='Sales Contract', domain="[('status', '=', True)]")

class SalesContractFieldReciept(models.Model):
    _inherit = 'stock.move'

    # order_id = fields.Many2one('purchase.order.line', string='Order Reference')
    note = fields.Char(string='Note')
    sales_contract = fields.Many2one('sales.contract', string='Sales Contract', domain="[('status', '=', True)]")



