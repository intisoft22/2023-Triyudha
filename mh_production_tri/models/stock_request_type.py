from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare


class StockRequestType(models.Model):
    _inherit = 'stock.request.type'

    delivery_prod = fields.Boolean('Delivery of Production')