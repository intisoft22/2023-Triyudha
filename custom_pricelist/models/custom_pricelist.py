from odoo import api, fields, models, _
from datetime import timedelta

class CustomPricelist(models.Model):
    _inherit = 'product.pricelist'

    customer_multi_id = fields.Many2many('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")
    customer_id = fields.Many2one('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date', readonly=True)
    exclude_tax = fields.Boolean(string='Exclude Tax', default=True)
    base_price_id = fields.Many2one('product.base.price.customer', string='Base Price')
    total_price = fields.Float(string="Total Price", compute="_compute_total_price")
    editable_total_price = fields.Boolean(string='Editable Total Price', default=False)
    product_weight = fields.Float(string='Product Weight')
    base_price = fields.Float(string="Base Price")
    calculated_price = fields.Float(string="Calculated Price", compute="_compute_calculated_price")

    approval_status = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Approved'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Approval Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    history_ids = fields.One2many('custom.pricelist.history', 'pricelist_id', string='Pricelist History')
    compute_price_method_pricelist = fields.Selection([
        ('base', 'Update Base price By Customer'),
        ('inc/dec', 'Increase/Decrease Base Price By Type')
    ], string='Compute Price Method')
    compute_price_method_multi_pricelist = fields.Selection([
        ('base', 'Update Base price By Customer'),
        ('inc/dec', 'Increase/Decrease Base Price By Type')
    ], string='Compute Price Method')
    base_ids = fields.One2many('product.base', 'pricelist_id', string="Base")
    inc_dec_ids = fields.One2many('product.inc_dec', 'pricelist_id', string="Increase/Decrease")

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
                if item.product_id == product_201 and hasattr(self.customer_id, 'price_201'):
                    item.fixed_price = self.customer_id.price_201
                elif item.product_id == product_304 and hasattr(self.customer_id, 'price_304'):
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

    def button_calculate_total_price(self):
        for record in self:
            record._compute_total_price()
            record.editable_total_price = True

        # Hitung pricelist per produk
        for item in record.item_ids:
            item.calculated_price = item.product_id.weight * record.base_price
    
    def update_base_price(self):
        for record in self:
            for item in record.item_ids:
                product = item.product_id
                old_base_price = product.lst_price

                if record.compute_price_method == 'inc/dec':
                    new_base_price = old_base_price + record.price_difference
                else:
                    new_base_price = old_base_price

                product.lst_price = product.weight * new_base_price

    @api.depends('item_ids', 'item_ids.product_id', 'item_ids.pricelist_id.base_price')
    def _compute_calculated_price(self):
        for record in self:
            total_calculated_price = 0.0
            for item in record.item_ids:
                if item.pricelist_id.compute_price_method == 'base':
                    total_calculated_price += item.product_id.weight * item.pricelist_id.base_price
                elif item.pricelist_id.compute_price_method == 'inc/dec':
                    total_calculated_price += item.product_id.weight * (item.pricelist_id.base_price + item.pricelist_id.price_difference)
            record.calculated_price = total_calculated_price

    @api.depends('item_ids.fixed_price')
    def _compute_total_price(self):
        for record in self:
            total = sum(item.fixed_price for item in record.item_ids)
            record.total_price = total

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
                elif item.compute_price == 'inc/dec':
                    # Jika pricelist menggunakan penurunan/menaikkan harga berdasarkan tipe
                    for inc_dec in pricelist.inc_dec_ids:
                        if inc_dec.type == '201':
                            base_price += inc_dec.price_difference
                        elif inc_dec.type == '304':
                            base_price -= inc_dec.price_difference

                    item.calculated_price = base_price

        return True



class CustomPricelistHistory(models.Model):
    _name = 'custom.pricelist.history'
    _description = 'Custom Pricelist History'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', readonly=True)
    start_date = fields.Date(string='Start Date', readonly=True)
    end_date = fields.Date(string='End Date', readonly=True)
    price = fields.Float(string='Price')

class ProductBase(models.Model):
    _name = 'product.base'
    _description = 'Product Base'

    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    customer_id = fields.Many2many('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")
    type_spec = fields.Selection([('201', '201'), ('304', '304'), ], string='Type', )
    bentuk = fields.Selection([('bulat', 'Bulat'), ('kotak', 'Kotak'), ], string='Bentuk', )
    # dia = fields.Float('Diameter (mm)')
    # dia_inc = fields.Float('Diameter (inc)')
    # panjang = fields.Float('Panjang (mm)')
    # lebar = fields.Float('Lebar (mm)')
    # tebal = fields.Float('Tebal (mm)')
    # Definisikan field lainnya yang ingin Anda tampilkan di tabel base

class ProductIncDec(models.Model):
    _name = 'product.inc_dec'
    _description = 'Product Increase/Decrease'

    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    customer_id = fields.Many2many('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")
    type_spec = fields.Selection([('201', '201'), ('304', '304')], string='Type')
    price_difference = fields.Float(string="Price Difference")
    bentuk = fields.Selection([('bulat', 'Bulat'), ('kotak', 'Kotak'), ], string='Bentuk', )
    # dia = fields.Float('Diameter (mm)')
    # dia_inc = fields.Float('Diameter (inc)')
    # panjang = fields.Float('Panjang (mm)')
    # lebar = fields.Float('Lebar (mm)')
    # tebal = fields.Float('Tebal (mm)')
    # Definisikan field lainnya yang ingin Anda tampilkan di tabel inc/dec