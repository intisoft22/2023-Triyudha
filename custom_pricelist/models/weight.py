from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    custom_weight = fields.Float('Custom Weight')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    custom_weight = fields.Float('Custom Weight', related='product_id.custom_weight')

    @api.depends('product_uom_qty', 'custom_weight')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if line.order_id.company_id.tax_calculation_rounding_method == 'round_globally':
                line.price_total = line.order_id.currency_id.round(line.price_total)
