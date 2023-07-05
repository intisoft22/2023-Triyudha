from odoo import fields, models, api

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'


    customer_id = fields.Many2one('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date', readonly=True)
    exclude_tax = fields.Boolean(string='Exclude Tax', default=True)

    price_method = fields.Selection([
        ('base', 'Update Base price By Customer'),
        ('inc/dec', 'Increase/Decrease Base Price By Type')
    ], string='Compute Price Method')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Approved'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='State', readonly=True, copy=False, index=True, tracking=3, default='draft')