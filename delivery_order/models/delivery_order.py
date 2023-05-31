from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sopir = fields.Char(string="Sopir")
    no_polisi = fields.Many2one('fleet.vehicle', string="Nomor Polisi")
    non = fields.Boolean(string="Non Tax")
    no_surat_jalan = fields.Char(string="No Surat Jalan", readonly=True, copy=False)

    @api.model
    def create(self, vals):
        if vals.get('non'):
            # No Surat Jalan Non
            vals['no_surat_jalan'] = self.env['ir.sequence'].next_by_code('stock.picking.non') or _('New')
        else:
            # No Surat Jalan Tax
            vals['no_surat_jalan'] = self.env['ir.sequence'].next_by_code('stock.picking.tax') or _('New')
        return super(StockPicking, self).create(vals)
