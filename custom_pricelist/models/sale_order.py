from odoo import api, fields, models, _


class SalesOrderCustom(models.Model):
    _inherit = 'sale.order'

    start_date = fields.Date(string='Schedule Date')
    categ_id = fields.Many2one('product.category', string='Produk Kategori', states={'draft': [('readonly', False)]},
                               readonly=True, required=True, )