from odoo import fields, models, api
from datetime import timedelta
import json

class MultiCustomerBasePrice(models.Model):
    _name = 'multi.customer.base.price'
    _description = 'Customer Base Price'

    pricelist_id = fields.Many2one('multi.product.pricelist', string='Pricelist')
    customer_ids = fields.Many2many('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")
    customer_id = fields.Many2one('res.partner', string='Customer')
    type = fields.Many2one('product.type', 'Type')
    bentuk = fields.Selection([('bulat', 'Bulat'), ('kotak', 'Kotak'), ], string='Bentuk', )
    base_price = fields.Float('Base Price')
    customer_id_domain = fields.Char(
        compute="_compute_customer_domain",
        readonly=True,
        store=False,
    )

    @api.depends('customer_ids')
    def _compute_customer_domain(self):
        for rec in self:
            if rec.customer_ids:

                customer_array = []
                for x in rec.customer_ids:
                    customer_array.append(x._origin.id)

                # return {'domain': {'product_id': [('id', 'in', product_array)]}}
                print(customer_array)
                rec.customer_id_domain = json.dumps(
                    [('id', 'in', customer_array)]
                )
            else:
                # return {'domain': {'product_id': [('id', '=', 0)]}}
                rec.customer_id_domain = json.dumps(
                    [('id', '=', 0)]
                )

class MultiCustomerChangePrice(models.Model):
    _name = 'multi.customer.change.price'
    _description = 'Customer Base Price'

    pricelist_id = fields.Many2one('multi.product.pricelist', string='Pricelist')
    customer_ids = fields.Many2many('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")
    customer_id = fields.Many2one('res.partner', string='Customer')
    type = fields.Many2one('product.type', 'Type')
    bentuk = fields.Selection([('bulat', 'Bulat'), ('kotak', 'Kotak'), ], string='Bentuk', )
    inc_dec_price = fields.Float('Increase/Decrease Price')

    customer_id_domain = fields.Char(
        compute="_compute_customer_domain",
        readonly=True,
        store=False,
    )

    @api.depends('customer_ids')
    def _compute_customer_domain(self):
        for rec in self:
            if rec.customer_ids:

                customer_array = []
                for x in rec.customer_ids:
                    customer_array.append(x._origin.id)

                # return {'domain': {'product_id': [('id', 'in', product_array)]}}
                print(customer_array)
                rec.customer_id_domain = json.dumps(
                    [('id', 'in', customer_array)]
                )
            else:
                # return {'domain': {'product_id': [('id', '=', 0)]}}
                rec.customer_id_domain = json.dumps(
                    [('id', '=', 0)]
                )

class ProductPricelist(models.Model):
    _name = 'multi.product.pricelist'
    _description = 'Multi Product Pricelist'

    name=fields.Char('Name')
    customer_id = fields.Many2many('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date', readonly=True)
    exclude_tax = fields.Boolean(string='Exclude Tax', default=True)

    price_method = fields.Selection([
        ('base', 'Update Base price By Customer'),
        ('incdec', 'Increase/Decrease Base Price By Type')
    ], string='Compute Price Method')

    base_price_ids = fields.One2many('multi.customer.base.price', 'pricelist_id', string='Base Price')
    change_price_ids = fields.One2many('multi.customer.change.price', 'pricelist_id', string='Increase/Decrease Price')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Approved'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='State', readonly=True, copy=False, index=True, tracking=3, default='draft')
    item_ids = fields.One2many(
        'product.pricelist', 'multipricelist_id', 'Pricelist Items',
        copy=True)

    def action_submit(self):
        for x in self:
            x.state = 'waiting'

    def action_approve(self):
        for x in self:
            x.state = 'approved'
            if not x.customer_id:
                pricelist = self.env['product.pricelist'].search(
                    [('state', '=', 'approved'), ('end_date', '=', False)], order='start_date desc', limit=1)
            else:

                pricelist = self.env['product.pricelist'].search(
                    [('state', '=', 'approved'), ('end_date', '=', False), ('customer_id', '=', x.customer_id.id)],
                    order='start_date desc', limit=1)
                if not pricelist:
                    pricelist = self.env['product.pricelist'].search(
                        [('state', '=', 'approved'), ('end_date', '=', False)], order='start_date desc', limit=1)
            if pricelist:
                if x.customer_id and pricelist.customer_id:
                    pricelist[0].end_date=x.start_date-timedelta(days=1)
                    for item in pricelist[0].item_ids:
                        item.end_date=x.start_date-timedelta(days=1)

    def action_draft(self):
        for x in self:
            x.state = 'draft'

    def action_cancel(self):
        for x in self:
            x.state = 'cancel'

    def action_compute(self):
        for record in self:
            if record.item_ids:
                for item in record.item_ids:
                    item.unlink()
            if record.customer_id:
                for cust in record.customer_id:
                    arraybase=[]
                    for base in record.base_price_ids:
                        if base.customer_id.id == cust.id:
                            arraybase.append(
                                (0, 0, {
                                    'type': base.type.id,
                                    'bentuk': base.bentuk,
                                    'base_price': base.base_price,
                                })
                            )
                    arraychange=[]
                    for base in record.change_price_ids:
                        if base.customer_id.id == cust.id:
                            arraychange.append(
                                (0, 0, {
                                    'type': base.type.id,
                                    'bentuk': base.bentuk,
                                    'inc_dec_price': base.inc_dec_price,
                                })
                            )
                    vals = {
                        'name': record.name,
                        'customer_id': cust.id,
                        'start_date': record.start_date,
                        'end_date': record.end_date,
                        'exclude_tax': record.exclude_tax,
                        'price_method': record.price_method,
                        'multipricelist_id': record.id,
                        'base_price_ids': arraybase,
                        'change_price_ids': arraychange,
                    }
                    pricelist=self.env['product.pricelist'].create(vals)
                    pricelist.action_compute()





