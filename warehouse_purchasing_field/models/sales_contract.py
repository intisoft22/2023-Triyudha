# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SalesContractField(models.Model):
    _inherit = "purchase.order.line"


    sales_contract = fields.Many2one('sales.contract', string='sales contract', domain="[('status', '=', True)]")

