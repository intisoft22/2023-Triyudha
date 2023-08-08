from odoo import fields, models, api
from datetime import timedelta

class CustomerBasePrice(models.Model):
    _name = 'customer.base.price'
    _description = 'Customer Base Price'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    customer_id = fields.Many2one('res.partner', string='Customer')
    type = fields.Many2one('product.type', 'Type')
    bentuk = fields.Selection([('bulat', 'Bulat'), ('kotak', 'Kotak'), ], string='Bentuk', )
    base_price = fields.Float('Base Price')


class CustomerChangePrice(models.Model):
    _name = 'customer.change.price'
    _description = 'Customer Base Price'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    customer_id = fields.Many2one('res.partner', string='Customer')
    type = fields.Many2one('product.type', 'Type')
    bentuk = fields.Selection([('bulat', 'Bulat'), ('kotak', 'Kotak'), ], string='Bentuk', )
    inc_dec_price = fields.Float('Increase/Decrease Price')


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    multipricelist_id = fields.Many2one('multi.product.pricelist', string='Pricelist')
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
            if record.price_method == 'base':
                for base in record.base_price_ids:
                    product_ids = self.env['product.product'].search(
                        [('typespec', '=', base.type.id), ('bentuk', '=', base.bentuk)])
                    for p in product_ids:
                        vals = {
                            'product_tmpl_id': p.product_tmpl_id.id,
                            'product_id': p.id,
                            'min_quantity': 1,
                            'fixed_price': base.base_price*p.weight,
                            'date_start': record.start_date,
                            'pricelist_id': record.id,
                        }
                        self.env['product.pricelist.item'].create(vals)
            elif record.price_method == 'incdec':
                changes={}
                for base in record.change_price_ids:
                    if base.type.id not in changes:
                        changes[base.type.id]={}
                        if base.bentuk not in changes[base.type.id]:
                            changes[base.type.id][base.bentuk] = base.inc_dec_price
                if not record.customer_id:
                    pricelist = self.env['product.pricelist'].search(
                        [('state', '=', 'approved'), ('end_date', '=', False)],order='start_date desc',limit=1)
                else:

                    pricelist = self.env['product.pricelist'].search(
                        [('state', '=', 'approved'), ('end_date', '=', False), ('customer_id', '=', record.customer_id.id)],order='start_date desc',limit=1)
                    if not pricelist:
                        pricelist = self.env['product.pricelist'].search(
                            [('state', '=', 'approved'), ('end_date', '=', False)],order='start_date desc',limit=1)
                if pricelist:
                    for base in pricelist.base_price_ids:
                        product_ids = self.env['product.product'].search(
                            [('typespec', '=', base.type.id), ('bentuk', '=', base.bentuk)])
                        for p in product_ids:
                            vals = {
                                'product_tmpl_id': p.product_tmpl_id.id,
                                'product_id': p.id,
                                'min_quantity': 1,
                                'fixed_price': (base.base_price + changes[base.type.id][base.bentuk])* p.weight,
                                'date_start': record.start_date,
                                'pricelist_id': record.id,
                            }
                            self.env['product.pricelist.item'].create(vals)


