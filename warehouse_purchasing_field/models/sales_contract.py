# -*- coding: utf-8 -*-
from odoo import api, fields, models
class SalesContractField(models.Model):
    _inherit = 'purchase.order.line'

    sales_contract = fields.Many2one('sales.contract', string='Sales Contract', domain="[('status', '=', True)]")

class SalesContractFieldReciept(models.Model):
    _inherit = 'stock.move'

    note = fields.Char(string='Note')
    sales_contract = fields.Many2one('sales.contract', string='Sales Contract')

