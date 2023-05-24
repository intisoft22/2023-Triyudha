from odoo import models, fields

class GenerateMultiPricelist(models.Model):
    _name = 'generate.multi.pricelist'
    _description = 'Generate Multi Pricelist'

    customer_id = fields.Many2many('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date', readonly=True)
    exclude_tax = fields.Boolean(string='Exclude Tax', default=True)
    approval_status = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Approved'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Approval Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    history_ids = fields.One2many('custom.pricelist.history', 'pricelist_id', string='Pricelist History')
    compute_price_method = fields.Selection([
        ('increase', 'Increase'),
        ('decrease', 'Decrease')
    ], string='Compute Price Method', default='increase')
