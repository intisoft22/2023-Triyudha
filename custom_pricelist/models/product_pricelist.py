# from odoo import models, fields, api, exceptions

# class SaleOrder(models.Model):
#     _inherit = 'sale.order'

#     start_date = fields.Date(string='Start Date')

# class ProductPricelistItem(models.Model):
#     _inherit = 'product.pricelist.item'

#     start_date = fields.Date(string='Start Date')


#     @api.constrains('order_line', 'start_date')
#     def _check_start_date(self):
#         for record in self:
#             for line in record.order_line:
#                 if line.start_date != record.start_date:
#                     raise exceptions.ValidationError("Start Date on line must be the same as the header Start Date.")
