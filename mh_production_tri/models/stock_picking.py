from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare

from datetime import datetime
from lxml import etree

import json

# class StockPickingType(models.Model):
#     _inherit = 'stock.picking.type'
#     production=fields.Boolean('Production?')

class stock_picking(models.Model):
    _inherit = 'stock.picking'


    delivery_prod = fields.Boolean('Delivery of Production')

    # check_user = fields.Boolean(
    #     string="Check User", store=True,
    #     compute="_get_checkuser"
    # )
    # check_user2 = fields.Boolean(
    #     string="Check User",
    #     compute="_get_checkuser"
    # )

    def write(self, vals):
        delivery_prod = False
        if vals.get('delivery_prod'):
            delivery_prod = vals.get('delivery_prod')
        else:
            delivery_prod = self.delivery_prod
        if delivery_prod:
            # print(vals.get('move_ids_without_package'))
            if vals.get('move_ids_without_package'):
                item = vals.get('move_ids_without_package')
                for i in item:
                    i2 = i[2]
                    if i2:
                        if i2.get('note', 0.0):
                            note = i2.get('note', 0.0)
                            # print(note)
                            res = super(stock_picking, self).write(vals)
                            return res
                raise UserError(_("  you can't add an other items "))
            else:
                res = super(stock_picking, self).write(vals)
                return res
        else:

            res = super(stock_picking, self).write(vals)
            return res
    #
    # @api.depends('picking_type_id')
    # def _get_checkuser(self):
    #     for x in self:
    #
    #         x.check_user2 = False
    #         if x.picking_type_id.production == "draft":
    #             if x.create_uid.id == self.env.user.id:
    #                 x.check_user2 = True
    #         if x.state == "submitted":
    #
    #             if self.env.user.has_group('in_warehouse.group_confirm_sr'):
    #                 wh = []
    #                 for b in self.env.user.branch_ids:
    #                     wh.append(b.id)
    #
    #                 if self.warehouse_id.id in wh:
    #                     x.check_user2 = True
    #         if x.state == 'review':
    #             wh_review = []
    #             for r in self.env.user.route_ids:
    #                 wh_review.append(r.id)
    #             if self.env.user.has_group('in_warehouse.group_review_sr') and x.route_id.id in wh_review:
    #                 x.check_user2 = True

class StockMove(models.Model):
    _inherit = 'stock.move'
    delivery_prod = fields.Boolean('Delivery of Production')