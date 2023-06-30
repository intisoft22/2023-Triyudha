# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Sales(models.Model):
    _inherit = "sale.order"

