from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare


class StockRequestType(models.Model):
    _name = 'stock.request.type'
    _description ="Stock Request Type"

    route_id = fields.Many2many('stock.location.route', string='Route', required=True)
    categ_id = fields.Many2many('product.category', string='Product Category', required=True)

    name = fields.Char('Name', required=True)
    initial = fields.Char('Initial', required=True)
    category = fields.Selection([
        ('warehouse', 'Inter Warehouse'),
        ('location', 'Inter Location'),
    ], string='Category', required=True)
