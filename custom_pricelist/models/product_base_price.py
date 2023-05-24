from odoo import fields, models, api

class ProductBasePriceCustomer(models.Model):
    _name = 'product.base.price.customer'
    
    customer_id = fields.Many2one('res.partner', string='Customer')
    type = fields.Selection(selection=lambda r: [(201, '201'), (304, '304')], string='Type')
    base_price = fields.Float('Base Price')


class ProductPriceChangeType(models.Model):
    _name = 'product.price.change.type'
    
    type = fields.Selection(selection=lambda r: [(201, '201'), (304, '304')], string='Type')
    price_change = fields.Float('Price Change')


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    
    base_price_id = fields.Many2one('product.base.price.customer', string='Base Price')
    price_change_id = fields.Many2one('product.price.change.type', string='Price Change')

    @api.model
    def create(self, vals):
        base_price_id = vals.get('base_price_id')
        price_change_id = vals.get('price_change_id')

        if base_price_id and price_change_id:
            base_price = self.env['product.base.price.customer'].browse(base_price_id)
            price_change = self.env['product.price.change.type'].browse(price_change_id)
            vals['fixed_price'] = base_price.base_price + price_change.price_change
        return super().create(vals)

    def write(self, vals):
        if 'base_price_id' in vals or 'price_change_id' in vals:
            base_price = self.env['product.base.price.customer'].browse(vals.get('base_price_id', self.base_price_id.id))
            price_change = self.env['product.price.change.type'].browse(vals.get('price_change_id', self.price_change_id.id))
            vals['fixed_price'] = base_price.base_price + price_change.price_change
        return super().write(vals)
