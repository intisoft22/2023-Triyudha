import json

# -*- coding: utf-8 -*-


from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    up_contact = fields.Many2one('res.partner',  readonly=False, string="Up Contact")
    up_contact_domain = fields.Char(
        compute="_compute_up_contact_domain",
        readonly=True,
        store=False,
    )

    product_category = fields.Many2one('product.category', string="Product Category", domain=[('parent_id', '=', False)], required=True)
    shipment_term = fields.Char(string='Shipment Term')
    others = fields.Char(string='Others')
    deliver_to_domain = fields.Char(
        compute="_compute_deliver_to_domain",
        readonly=True,
        store=False,
    )

    name_up_contact = fields.Char(
        compute="_compute_name_up_contact",
        readonly=True,
        store=False,
    )

    @api.onchange('product_category')
    def _onchange_product_category(self):
        for rec in self:
            rec.order_line = False
            rec.picking_type_id = False

    @api.onchange('product_category')
    def _compute_deliver_to_domain(self):
        for rec in self:
            if rec.product_category:
                rec.deliver_to_domain = json.dumps([
                    ('code', '=', 'incoming'),
                    ('product_category', 'child_of', rec.product_category.id),
                    '|',
                    ('warehouse_id', '=', False),
                    ('warehouse_id.company_id', '=', rec.company_id.id),
                    ])
            else:
                rec.deliver_to_domain = json.dumps([
                    ('code', '=', 'incoming'),
                    ('product_category', 'child_of', 0),
                    '|',
                    ('warehouse_id', '=', False),
                    ('warehouse_id.company_id', '=', rec.company_id.id),
                    ])

    @api.onchange('partner_id')
    def _compute_up_contact_domain(self):
        for rec in self:
            if rec.partner_id:
                rec.up_contact_domain = json.dumps([
                    ('parent_id', '=', rec.partner_id.id),
                    ('active', '=', True),
                    ('type', '=', 'contact'),
                ])
            else:
                rec.up_contact_domain = json.dumps([
                    ('parent_id', '=', 0),
                    ('active', '=', True),
                    ('type', '=', 'contact'),
                ])

    @api.onchange('up_contact')
    def _compute_name_up_contact(self):
        for rec in self:
            rec.name_up_contact = rec.up_contact.name



class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_category = fields.Many2one('product.category', string="Product Category", domain=[('parent_id', '=', False)])
    note = fields.Char(string='Note')

    product_id_domain = fields.Char(
        compute="_compute_product_id_domain",
        readonly=True,
        store=False,
    )

    @api.onchange('product_category')
    def _compute_product_id_domain(self):
        for rec in self:
            if rec.product_category:
                rec.product_id_domain = json.dumps([
                    ('purchase_ok', '=', True),
                    ('categ_id', 'child_of', rec.product_category.id),
                    '|',
                    ('company_id', '=', False),
                    ('company_id', '=', rec.company_id.id),
                    ])
            else:
                rec.product_id_domain = json.dumps([
                    ('purchase_ok', '=', True),
                    ('categ_id', 'child_of', 0),
                    '|',
                    ('company_id', '=', False),
                    ('company_id', '=', rec.company_id.id),
                ])


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    no_surat_supplier = fields.Char(string='No. Surat Jalan Supplier')


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    product_category = fields.Many2one('product.category', string="Product Category", domain=[('parent_id', '=', False)])

    
class ResPartner(models.Model):
    _inherit = 'res.partner'

    no_fax = fields.Char(string='No. Fax')

class ResCompany(models.Model):
    _inherit = 'res.company'

    no_fax = fields.Char(string='Fax')
    desc = fields.Text(string='Description')