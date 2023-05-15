from odoo import models, fields, api

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    product_weight = fields.Float('Product Weight')
    product_type = fields.Selection([('201', '201'), ('304', '304')], string='Product Type')

    @api.onchange('product_weight', 'product_type')
    def _onchange_price(self):
        # Set the price of the pricelist item based on the weight and type
        if self.product_weight and self.product_type:
            if self.product_type == '201':
                self.price = self.product_weight * 10  # Replace with your formula
            elif self.product_type == '304':
                self.price = self.product_weight * 20  # Replace with your formula
