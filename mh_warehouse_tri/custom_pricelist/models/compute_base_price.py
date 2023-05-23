from odoo import models, fields, api

class CustomerBasePrice(models.Model):
    _name = 'customer.base.price'
    _description = 'Customer Base Price'

    customer_id = fields.Many2one('res.partner', string='Customer')
    type = fields.Selection([('201', 'Type 201'), ('304', 'Type 304')], string='Type')
    base_price = fields.Float('Base Price')
    inc_dec_price = fields.Float('Increase/Decrease Price', compute='_compute_inc_dec_price')

    @api.depends('base_price')
    def _compute_inc_dec_price(self):
        for rec in self:
            if int(rec.type) == 201:
                rec.inc_dec_price = rec.base_price + 1000
            elif int(rec.type) == 304:
                rec.inc_dec_price = rec.base_price - 1500
