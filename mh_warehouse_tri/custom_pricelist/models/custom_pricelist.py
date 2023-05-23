from odoo import api, fields, models, _
from datetime import timedelta

class CustomPricelist(models.Model):
    _inherit = 'product.pricelist'

    customer_id = fields.Many2many('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date', readonly=True)
    exclude_tax = fields.Boolean(string='Exclude Tax', default=True)
    base_price_id = fields.Many2one('product.base.price.customer', string='Base Price')
    calculated_price = fields.Float(string='Calculated Price', compute='_compute_calculated_price', store=True)

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

    def action_waiting(self):
        self.approval_status = 'waiting'

    def action_approved(self):
        self.approval_status = 'approved'

    def action_draft(self):
        self.approval_status = 'draft'

    def action_cancel(self):
        self.approval_status = 'cancel'

    @api.onchange('customer_id')
    def _compute_price_by_product_type(self):
        product_201 = self.env['product.product'].search([('name', '=', 'Product 201')], limit=1)
        product_304 = self.env['product.product'].search([('name', '=', 'Product 304')], limit=1)

        if self.customer_id:
            for item in self.item_ids:
                if item.product_id == product_201:
                    item.fixed_price = self.customer_id.price_201
                elif item.product_id == product_304:
                    item.fixed_price = self.customer_id.price_304

    def action_approve(self):
        self.write({'approval_status': 'approved'})

    def write(self, vals):
        if 'start_date' in vals:
            if not vals.get('customer_id'):
                existing_pricelist = self.env['product.pricelist'].search([
                    ('customer_id', '=', False),
                    ('approval_status', '=', 'approved')
                ], order='start_date desc', limit=1)

                if existing_pricelist:
                    vals['end_date'] = existing_pricelist.start_date - timedelta(days=1)

            elif vals['customer_id']:
                existing_pricelist = self.env['product.pricelist'].search([
                    ('customer_id', 'in', vals['customer_id']),
                    ('approval_status', '=', 'approved')
                ], order='start_date desc', limit=1)

                if existing_pricelist:
                    vals['end_date'] = existing_pricelist.start_date - timedelta(days=1)

        return super(CustomPricelist, self).write(vals)

    # calculate
    # @api.depends('item_ids', 'item_ids.calculated_price')
    # def _compute_calculated_price(self):
    #     for pricelist in self:
    #         pricelist.calculated_price = sum(pricelist.item_ids.mapped('calculated_price'))

    def calculate_pricelist(self):
        for pricelist in self:
            for item in pricelist.item_ids:
                # Dapatkan produk terkait dengan item pricelist
                product = item.product_id

                # Dapatkan harga dasar produk
                base_price = product.lst_price

                # Logika perhitungan harga berdasarkan metode perhitungan lainnya
                if item.compute_price == 'fixed_price':
                    # Jika pricelist menggunakan harga tetap
                    item.calculated_price = item.price_surcharge

        return True



class CustomPricelistHistory(models.Model):
    _name = 'custom.pricelist.history'
    _description = 'Custom Pricelist History'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', readonly=True)
    start_date = fields.Date(string='Start Date', readonly=True)
    end_date = fields.Date(string='End Date', readonly=True)
    price = fields.Float(string='Price')
