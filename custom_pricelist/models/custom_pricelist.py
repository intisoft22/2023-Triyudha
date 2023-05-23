from odoo import api, fields, models, _
from datetime import timedelta

class CustomPricelist(models.Model):
    _inherit = 'product.pricelist'

    customer_id = fields.Many2one('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    include_tax = fields.Boolean(string='Include Tax')
    approval_status = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Approved'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Approval Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    history_ids = fields.One2many('custom.pricelist.history', 'pricelist_id', string='Pricelist History')
    
    def action_waiting(self):
        self.approval_status = 'waiting'

    def action_approved(self):
        self.approval_status = 'approved'
    
    def action_draft(self):
        self.approval_status = 'draft'
    
    def action_cancel(self):
        self.approval_status = 'cancel'

    # Tambahkan fungsi untuk menghitung harga produk berdasarkan jenis barang (201 dan 304)
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

    # Fungsi untuk menghandle approval satu tingkat
    def action_approve(self):
        self.write({'approval_status': 'approved'})

    # Fungsi untuk menghandle perubahan pricelist sesuai ketentuan yang diberikan
    def write(self, vals):
        if 'start_date' in vals:
            # Jika ada pricelist baru, tanggal akhir berlaku pricelist lama akan terisi sama dengan tanggal mulai berlaku pada pricelist yang baru
            self.end_date = vals['start_date'] - timedelta(days=1)
        return super(CustomPricelist, self).write(vals)

# class SaleOrder(models.Model):
#     _inherit = 'sale.order'

#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('waiting_approval', 'Waiting Approval'),
#         ('approved', 'Approved'),
#         ('cancel', 'Cancelled'),
#     ], string='Status', default='draft', readonly=True, copy=False)

#     def action_submit_for_approval(self):
#         self.ensure_one()
#         self.state = 'waiting_approval'

#     def action_approve_order(self):
#         self.ensure_one()
#         self.state = 'approved'

class CustomPricelistHistory(models.Model):
    _name = 'custom.pricelist.history'
    _description = 'Custom Pricelist History'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    price = fields.Float(string='Price')
