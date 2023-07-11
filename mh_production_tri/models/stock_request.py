from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare
from datetime import datetime

from lxml import etree

import json



class StockRequest(models.Model):
    _inherit = 'stock.request'

    delivery_prod = fields.Boolean('Delivery of Production')

    def _action_launch_procurement_rule(self):
        res = super()._action_launch_procurement_rule()
        picking = self.env['stock.picking'].search([
            ('group_id', '=', self.procurement_group_id.id)])
        if picking:
            for p in picking:

                deliv = False
                if 'Production' in p.picking_type_id.name and 'Receive' in p.picking_type_id.name and 'Material' not in p.picking_type_id.name:
                    p.write({
                        'delivery_prod': True,

                    })
                    deliv = True
                for m in p.move_ids_without_package:
                    if deliv:
                        m.delivery_prod = True
                    # if m.product_id.id == request.product_id.id:
                    #     m.note = request.note

        return res

class StockRequestOrder(models.Model):
    _inherit = 'stock.request.order'

    delivery_prod = fields.Boolean('Delivery of Production')

    type_id_domain = fields.Char(
        compute="_compute_type_id_domain",
        readonly=True,
        store=False,
    )



    @api.depends('requested_by','delivery_prod')
    def _compute_type_id_domain(self):
        for rec in self:
            print(rec.delivery_prod)
            if rec.delivery_prod:

                rec.type_id_domain = json.dumps(
                    [('delivery_prod', '=', True)]
                )
            else:
                # return {'domain': {'product_id': [('id', '=', 0)]}}
                rec.type_id_domain = json.dumps(
                    [('delivery_prod', '!=', True)]
                )


    def action_confirm(self):

        for sro in self:

            if not sro.delivery_prod:

                res = super().action_confirm()
                return res
            else:
                sro.action_create_pengiriman()


    def action_create_pengiriman(self):

        for sro in self:
            if sro.delivery_prod:
                vals = {}
                proc_group_obj = self.env['procurement.group']
                vals['date_planned'] = sro.expected_date
                id_group = proc_group_obj.create(
                    vals)
                # print(id_group)
                order_proc_group_to_use = \
                    sro.procurement_group_id = id_group.id

                for x in sro.stock_request_ids:
                    x.procurement_group_id = order_proc_group_to_use
                self.mapped('stock_request_ids').action_confirm()
                sro.write({'state': 'open'})
                # print(sro.picking_ids)

                picking = self.env['stock.picking'].search([
                    ('group_id', '=', order_proc_group_to_use)],order='id desc')
                if picking:
                    for p in picking:


                        if p.location_id.id == sro.src_location_id.id:
                            p.action_assign()
                            # print(p.state)
                            # for m in p.move_ids_without_package:
                            #     for ml in m.move_line_ids:
                            #         ml.lot_name=sro.lot_id
                            if p.state == 'assigned':
                                p.button_validate()
                                sro.check_done()


    check_user = fields.Boolean(
        string="Check User", store=True,
        compute="_get_checkuser"
    )
    check_user2 = fields.Boolean(
        string="Check User",
        compute="_get_checkuser"
    )

    @api.depends('create_uid', 'src_warehouse_id', 'warehouse_id')
    def _get_checkuser(self):
        for x in self:

            x.check_user2 = False
            if x.state == "draft":
                if x.create_uid.id == self.env.user.id:
                    x.check_user2 = True
            if x.state == "submitted":
                if x.delivery_prod:

                    if self.env.user.has_group('mrp.group_mrp_user'):
                        x.check_user2 = True
                else:


                    if self.env.user.has_group('mh_warehouse_tri.group_confirm_sr'):

                        x.check_user2 = True


class StockRequestOrderProd(models.Model):

    _name = 'stock.request.order.prod'
    _table = 'stock_request_order'
    _inherit = 'stock.request.order'
    _description = 'Receipts Production Result'


    prod_ref = fields.Integer('Dummy')

    delivery_prod = fields.Boolean('Delivery of Production',default=True)


    # lot_id = fields.Many2one(
    #     'stock.production.lot', 'Lot/Serial Number', readonly=True,required=True,
    #     states={'draft': [('readonly', False)]}, )
    @api.model
    def view_delivery_prod_branch(self):
        users = self.env['res.users'].search(
            [('id', '=', self.env.uid)], limit=1)
        sr_type_ids2 = self.env['stock.request.type'].search(
            [('delivery_prod', '=', True)])
        wh = []
        sr_type = []
        user_sr_type = []
        user_line_prod = []
        for u in users:
            for b in u.branch_ids:
                wh.append((b.id))
            for b in u.sr_type_ids:
                user_sr_type.append((b.id))
            for b in u.line_prod_ids:
                user_line_prod.append((b.id))
        # print (user_sr_type)
        for t in sr_type_ids2:
            if t.id in user_sr_type:
                sr_type.append(t.id)
        # print(sr_type)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.request.order.prod',
            'name': 'Delivery of Production',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'context': "{'search_default_group_state':1,'produksi':True,'default_delivery_prod':True}",
            'domain': "[('warehouse_id','in'," + str(wh) + "),('type_id','in'," + str(sr_type) + "),('lineprod_id','in'," + str(user_line_prod) + ")]",

        }


    check_user = fields.Boolean(
        string="Check User", store=True,
        compute="_get_checkuser"
    )
    check_user2 = fields.Boolean(
        string="Check User",
        compute="_get_checkuser"
    )

    @api.depends('create_uid', 'src_warehouse_id', 'warehouse_id')
    def _get_checkuser(self):
        for x in self:

            x.check_user2 = False
            if x.state == "draft":
                if x.create_uid.id == self.env.user.id:
                    x.check_user2 = True
            if x.state == "submitted":
                if x.delivery_prod:

                    if self.env.user.has_group('mrp.group_mrp_user'):
                        x.check_user2 = True
                else:


                    if self.env.user.has_group('mh_warehouse_tri.group_confirm_sr'):

                        x.check_user2 = True

    def action_cancel_open(self):
        self.sudo().mapped('move_ids')._action_cancel()
        self.write({'state': 'cancel'})
        return True

