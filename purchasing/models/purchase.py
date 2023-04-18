import json

# -*- coding: utf-8 -*-


from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    product_category = fields.Many2one('product.category', string="Product Category", domain=[('parent_id', '=', False)], required=True)
    shipment_term = fields.Char(string='Shipment Term')
    others = fields.Char(string='Others')
    deliver_to_domain = fields.Char(
        compute="_compute_deliver_to_domain",
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
                    # '|',
                    # ('warehouse_id', '=', False),
                    # ('warehouse_id.company_id', '=', 'company_id'),
                    ])
            else:
                rec.deliver_to_domain = json.dumps([
                    ('code', '=', 'incoming'),
                    ('product_category', 'child_of', 0),
                    # '|',
                    # ('warehouse_id', '=', False),
                    # ('warehouse_id.company_id', '=', 'company_id'),
                    ])

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_category = fields.Many2one('product.category', string="Product Category", domain=[('parent_id', '=', False)])

    product_id_domain = fields.Char(
        compute="_compute_product_id_domain",
        readonly=True,
        store=False,
    )

    @api.onchange('product_category')
    def _compute_product_id_domain(self):
        for rec in self:
            if rec.product_category:
                rec.product_id_domain = json.dumps([('categ_id', 'child_of', rec.product_category.id)])
            else:
                rec.product_id_domain = json.dumps([('categ_id', 'child_of', 0)])


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    no_surat_supplier = fields.Char(string='No. Surat Jalan Supplier')


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    product_category = fields.Many2one('product.category', string="Product Category", domain=[('parent_id', '=', False)])