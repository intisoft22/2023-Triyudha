from odoo import fields, models, api

class CustomerBasePrice(models.Model):
    _name = 'customer.base.price'
    _description = 'Customer Base Price'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    customer_id = fields.Many2one('res.partner', string='Customer')
    type =fields.Many2one('product.type','Type')
    bentuk = fields.Selection([('bulat', 'Bulat'), ('kotak', 'Kotak'), ], string='Bentuk', )
    base_price = fields.Float('Base Price')

class CustomerChangePrice(models.Model):
    _name = 'customer.change.price'
    _description = 'Customer Base Price'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    customer_id = fields.Many2one('res.partner', string='Customer')
    type =fields.Many2one('product.type','Type')
    bentuk = fields.Selection([('bulat', 'Bulat'), ('kotak', 'Kotak'), ], string='Bentuk', )
    inc_dec_price = fields.Float('Increase/Decrease Price')

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'


    customer_id = fields.Many2one('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date', readonly=True)
    exclude_tax = fields.Boolean(string='Exclude Tax', default=True)

    price_method = fields.Selection([
        ('base', 'Update Base price By Customer'),
        ('incdec', 'Increase/Decrease Base Price By Type')
    ], string='Compute Price Method')

    base_price_ids = fields.One2many('customer.base.price', 'pricelist_id', string='Base Price')
    change_price_ids = fields.One2many('customer.change.price', 'pricelist_id', string='Increase/Decrease Price')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Approved'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='State', readonly=True, copy=False, index=True, tracking=3, default='draft')