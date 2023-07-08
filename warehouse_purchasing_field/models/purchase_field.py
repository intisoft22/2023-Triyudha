# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SalesContract(models.Model):
    _name = "sales.contract"
    _description = "Sales Contract"

    name = fields.Char(string="Name", required="True")
    vendor = fields.Many2one('res.partner', string='Vendor', required=True, domain=[('parent_id', '=', False)])
    status = fields.Boolean(string="Status", default=True)

