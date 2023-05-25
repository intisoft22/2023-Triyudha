# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import json
from odoo.osv import expression

class StockLocation(models.Model):
    _inherit = 'stock.location'

    categ_id = fields.Many2one('product.category', string='Product Category')

