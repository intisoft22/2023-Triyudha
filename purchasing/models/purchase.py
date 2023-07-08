import json

# -*- coding: utf-8 -*-


from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    up_contact = fields.Many2one('res.partner', readonly=False, string="Up Contact")
    up_contact_domain = fields.Char(
        compute="_compute_up_contact_domain",
        readonly=True,
        store=False,
    )

    product_category = fields.Many2one('product.category', string="Product Category",
                                       domain=[('parent_id', '=', False)], required=True)
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

    receipt_state = fields.Selection([
        ('no', 'Nothing to Receive'),
        ('waiting', 'Waiting Receive'),
        ('partial', 'Partially Receive'),
        ('full', 'Fully Receive'),
    ], string='Receipt Status', compute='_get_receipt_status', store=True, readonly=True, copy=False, default='no')

    invoice_status = fields.Selection([
        ('no', 'Nothing to Bill'),
        ('to invoice', 'Waiting Bills'),
        ('invoiced', 'Fully Billed'),
        ('partial', 'Partially Bills'),
    ], string='Billing Status', compute='_get_invoiced', store=True, readonly=True, copy=False, default='no')

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

    @api.depends('state', 'order_line.qty_received')
    def _get_receipt_status(self):
        for order in self:
            if order.state not in ('purchase', 'done'):
                order.receipt_state = 'no'
            else:
                qty_receive = 0
                quantity = 0
                for ln in order.order_line:
                    qty_receive += ln.qty_received
                    quantity += ln.product_qty

                if qty_receive == 0:
                    order.receipt_state = 'waiting'
                elif qty_receive < quantity:
                    order.receipt_state = 'partial'
                elif qty_receive >= quantity:
                    order.receipt_state = 'full'

    @api.depends('state', 'order_line.qty_to_invoice', 'order_line.qty_invoiced')
    def _get_invoiced(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            if order.state not in ('purchase', 'done'):
                order.invoice_status = 'no'
                continue

            if any(
                    not float_is_zero(line.qty_to_invoice, precision_digits=precision)
                    for line in order.order_line.filtered(lambda l: not l.display_type)
            ):
                qty_invoiced = 0
                qty_received = 0
                for ln in order.order_line:
                    qty_invoiced += ln.qty_invoiced
                    qty_received += ln.qty_received

                if qty_invoiced == 0:
                    order.invoice_status = 'to invoice'
                elif qty_invoiced < qty_received:
                    order.invoice_status = 'partial'
                else:
                    order.invoice_status = 'to invoice'

            elif (
                    all(
                        float_is_zero(line.qty_to_invoice, precision_digits=precision)
                        for line in order.order_line.filtered(lambda l: not l.display_type)
                    )
                    and order.invoice_ids
            ):
                order.invoice_status = 'invoiced'
            else:
                order.invoice_status = 'no'


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_category = fields.Many2one('product.category', string="Product Category",
                                       domain=[('parent_id', '=', False)])
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


    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        res[0]['note'] = self.note
        res[0]['sales_contract'] = self.sales_contract.id
        return res

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    no_surat_supplier = fields.Char(string='No. Surat Jalan Supplier')

    def button_validate(self):
        picking_type = self.env['stock.picking.type'].search([('id', '=', self.picking_type_id.id)])

        res = super(StockPicking, self).button_validate()

        if res is True:
            if picking_type.code == 'incoming':
                self._set_as_2binvoiced()

        return res


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    product_category = fields.Many2one('product.category', string="Product Category",
                                       domain=[('parent_id', '=', False)])


class ResPartner(models.Model):
    _inherit = 'res.partner'

    no_fax = fields.Char(string='No. Fax')


class ResCompany(models.Model):
    _inherit = 'res.company'

    no_fax = fields.Char(string='Fax')
    desc = fields.Text(string='Description')


class StockInvoiceOnshipping(models.TransientModel):
    _inherit = 'stock.invoice.onshipping'

    def _get_invoice_line_values(self, moves, invoice_values, invoice):
        """
        Create invoice line values from given moves
        :param moves: stock.move
        :param invoice: account.move
        :return: dict
        """
        name = ", ".join(moves.mapped("name"))
        move = fields.first(moves)
        product = move.product_id
        fiscal_position = self.env["account.fiscal.position"].browse(
            invoice_values["fiscal_position_id"]
        )
        partner_id = self.env["res.partner"].browse(invoice_values["partner_id"])
        categ = product.categ_id
        inv_type = invoice_values["move_type"]
        if inv_type in ("out_invoice", "out_refund"):
            account = product.property_account_income_id
            if not account:
                account = categ.property_account_income_categ_id
        else:
            account = product.property_account_expense_id
            if not account:
                account = categ.property_account_expense_categ_id
        account = move._get_account(fiscal_position, account)
        quantity = 0
        move_line_ids = []
        for move in moves:
            qty = move.product_uom_qty
            loc = move.location_id
            loc_dst = move.location_dest_id
            # Better to understand with IF/ELIF than many OR
            if inv_type == "out_invoice" and loc.usage == "customer":
                qty *= -1
            elif inv_type == "out_refund" and loc_dst.usage == "customer":
                qty *= -1
            elif inv_type == "in_invoice" and loc_dst.usage == "supplier":
                qty *= -1
            elif inv_type == "in_refund" and loc.usage == "supplier":
                qty *= -1
            quantity += qty
            move_line_ids.append((4, move.id, False))
        taxes = moves._get_taxes(fiscal_position, inv_type)
        # price = moves._get_price_unit_invoice(inv_type, partner_id, quantity)
        price = move.purchase_line_id.price_unit  # change price_unit from product price to po price
        line_obj = self.env["account.move.line"]
        values = line_obj.default_get(line_obj.fields_get().keys())
        values.update(
            {
                "name": name,
                "account_id": account.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "quantity": quantity,
                "price_unit": price,
                "tax_ids": [(6, 0, taxes.ids)],
                "move_line_ids": move_line_ids,
                "move_id": invoice.id,
                "purchase_line_id": move.purchase_line_id.id,  # only modify this line to save purchase_line_id - mifta
            }
        )
        values = self._simulate_invoice_line_onchange(values, price_unit=price)
        values.update({"name": name})
        return values
