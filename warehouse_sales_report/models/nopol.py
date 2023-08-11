# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockPickingNoPol(models.Model):
    _inherit = "stock.picking"

    no_polisi = fields.Char(string="No Polisi")

