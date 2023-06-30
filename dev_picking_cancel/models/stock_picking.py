# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
from odoo import api, models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_round, float_is_zero
import random

from odoo.exceptions import UserError, AccessError

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    def action_cancel(self):
        # if self.picking_type_id.code == 'internal':
        if self.state == 'done' or 'confirmed':

            aman=True
            aman2=True
            if self.state == 'done':
                for move in self.move_lines:
                    if move.move_dest_ids:
                        for destmove in move.move_dest_ids:
                            if destmove.state != 'cancel':
                                aman2 = False
                    location = move.location_dest_id.id
                    if move.product_id.type == 'product':
                        # print(location)
                        # print(self.order_id.warehouse_id.pick_type_id.default_location_src_id.name)
                        if move.location_dest_id.usage == 'internal':
                            qty_onhand = move.product_id.with_context(location=location)._compute_quantities_dict(
                                self._context.get('lot_id'),
                                self._context.get('owner_id'),
                                self._context.get('package_id'),
                                self._context.get('from_date'),
                                self._context.get('to_date'))
                            # print(qty_onhand)
                            # print("teeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
                            onhand_qty = qty_onhand[move.product_id.id]['qty_available']
                            outgoing = qty_onhand[move.product_id.id]['outgoing_qty']
                            incoming = qty_onhand[move.product_id.id]['incoming_qty']
                            ready = onhand_qty - outgoing + incoming
                            selisih = ready - move.quantity_done
                            # print(selisih)
                            if selisih < 0:
                                aman = False

                if not aman2:
                    raise UserError(_("You cannot cancel this document! (Other document not cancelled)"))
                if not aman:
                    raise UserError(_("You cannot cancel this document! (More than ready quantity)"))

            for move in self.move_lines:
                move.quantity_done = 0
                move._action_cancel()
                # pack_op = self.env['stock.move'].sudo().search(
                #         [('picking_id', '=', move.picking_id.id), ('product_id', '=', move.product_id.id)])
                # move.set_quant_quantity(move, pack_op, move.picking_id.state)
                    
        res = super(stock_picking, self).action_cancel()
        account_pool = self.env['account.move']
        for move in self.move_ids_without_package:
            entry_name = self.name + ' - '+ move.product_id.name
            entry_s_name = self.name
            entry_names = [entry_name, entry_s_name]
            move_ids = account_pool.search([('ref', 'in', entry_names), ('state', '=', 'posted')])
            if move_ids:
                move_ids.sudo().button_draft()
                move_ids.sudo().button_cancel()

    def action_set_draft(self):
        move_obj = self.env['stock.move']
        for pick in self:
            ids2 = [move.id for move in pick.move_lines]
            moves = move_obj.browse(ids2)
            moves.sudo().action_draft()
            for move in moves:
                for m_line in move.move_line_ids:
                    m_line.unlink()
        return True


class stock_move(models.Model):
    _inherit = 'stock.move'

    def unlink_serial_number(self):
        if self.picking_type_id and self.picking_type_id.code == 'incoming':
            for line in self.move_line_ids:
                if line.lot_id:
                    line.lot_id.name = line.lot_id.name + '- Cancel - '+ str(random.randint(0,99999))
                    
                    
    def action_draft(self):
        res = self.write({'state': 'draft'})
        return res

    def dev_set_quantity(self, move_qty, stock_move):
        quant_pool = self.env['stock.quant']
        product = stock_move.product_id

        if stock_move.product_id.type == 'product':
            if stock_move.product_id.tracking == 'none':
                out_qaunt = quant_pool.sudo().search(
                    [('product_id', '=', product.id), ('location_id', '=', stock_move.location_id.id)])
                if not out_qaunt:
                    out_qaunt2 = quant_pool.sudo().create({
                        'product_id':product and product.id or False,
                        'location_id':stock_move.location_id and stock_move.location_id.id or False,
                        'quantity':0 + move_qty,
                        'product_uom_id':stock_move.product_uom and stock_move.product_uom.id or False,
                    })
                if out_qaunt:
                    out_qaunt[0].quantity = out_qaunt[0].quantity + move_qty
                    if out_qaunt[0].quantity == 0:
                            out_qaunt[0].unlink()

                out_qaunt = quant_pool.sudo().search(
                    [('product_id', '=', product.id), ('location_id', '=', stock_move.location_dest_id.id)])
                if not out_qaunt:
                    out_qaunt2 = quant_pool.sudo().create({
                        'product_id':product and product.id or False,
                        'location_id':stock_move.location_id and stock_move.location_id.id or False,
                        'quantity':0 - move_qty,
                        'product_uom_id':stock_move.product_uom and stock_move.product_uom.id or False,
                    })
                if out_qaunt:
                    out_qaunt[0].quantity = out_qaunt[0].quantity - move_qty
                    if out_qaunt[0].quantity == 0:
                            out_qaunt[0].unlink()


            else:
                for line in stock_move.move_line_ids:
                    out_qaunt = quant_pool.sudo().search(
                        [('product_id', '=', product.id), ('location_id', '=', stock_move.location_id.id),('lot_id','=',line.lot_id.id)])
                    if not out_qaunt:
                        out_qaunt2 = quant_pool.sudo().create({
                            'product_id':product and product.id or False,
                            'location_id':stock_move.location_id and stock_move.location_id.id or False,
                            'quantity':0+ line.qty_done,
                            'product_uom_id':stock_move.product_uom and stock_move.product_uom.id or False,
                            'lot_id':line.lot_id and line.lot_id.id or False,
                        })
                    if out_qaunt:
                        out_qaunt[0].quantity = out_qaunt[0].quantity + line.qty_done
                        if out_qaunt[0].quantity == 0:
                            out_qaunt[0].unlink()


                    out_qaunt = quant_pool.sudo().search(
                        [('product_id', '=', product.id), ('location_id', '=', stock_move.location_dest_id.id),('lot_id','=',line.lot_id.id)])
                    if not out_qaunt:
                        out_qaunt2 = quant_pool.sudo().create({
                            'product_id':product and product.id or False,
                            'location_id':stock_move.location_id and stock_move.location_id.id or False,
                            'quantity':0- line.qty_done,
                            'product_uom_id':stock_move.product_uom and stock_move.product_uom.id or False,
                            'lot_id':line.lot_id and line.lot_id.id or False,
                        })
                    if out_qaunt:
                        out_qaunt[0].quantity = out_qaunt[0].quantity - line.qty_done
                        if out_qaunt[0].quantity == 0:
                            out_qaunt[0].unlink()

    
    def set_quant_quantity(self, stock_move, pack_operation_ids, pic_state):
        for pack_operation_id in pack_operation_ids:
            move_qty = stock_move.product_uom_qty
            if stock_move.quantity_done:
                move_qty = stock_move.quantity_done
                
            if stock_move.quantity_done  and pic_state == 'done':
                if stock_move.sale_line_id:
                    if stock_move.sale_line_id.qty_delivered >=  move_qty:
                        stock_move.sale_line_id.qty_delivered = stock_move.sale_line_id.qty_delivered - move_qty
                    
                if stock_move.purchase_line_id:
                    if stock_move.purchase_line_id.qty_received >= move_qty:
                        stock_move.purchase_line_id.qty_received = stock_move.purchase_line_id.qty_received - move_qty
                # if stock_move.product_id.type == 'product':
                self.dev_set_quantity(move_qty, stock_move)
                
        return True

    def unlink_stock_valuation_layer(self,move_id):
        val_line_ids = self.env['stock.valuation.layer'].sudo().search([('stock_move_id','=',move_id.id)])
        for line in val_line_ids:
            line.unlink()
            
            
    def _action_cancel(self):
        for move in self:
            pic_state = move.picking_id.state
            if move.picking_id.state != 'done':
                move._do_unreserve()
                
            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
            if move.propagate_cancel:
                # print(all(state == 'cancel' for state in siblings_states))
                if all(state == 'cancel' for state in siblings_states):
                    # print(move.propagate)
                    # print("propagate")
                    # print(move.move_dest_ids)
                    move.move_dest_ids._action_cancel()
            # if all(state in ('done', 'cancel') for state in siblings_states):
            #     move.move_dest_ids.write({'procure_method': 'make_to_stock'})
            #     move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})

            # if move.picking_id.state == 'done' or 'confirmed' and move.picking_id.picking_type_id.code in ['incoming','outgoing']:
            if move.picking_id.state == 'done' or 'confirmed':
                pack_op = self.env['stock.move'].sudo().search(
                    [('picking_id', '=', move.picking_id.id), ('product_id', '=', move.product_id.id)])
                if move.state == 'done':
                    self.set_quant_quantity(move, pack_op, pic_state)

            # self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
            self.write({'state': 'cancel'})
            self.unlink_stock_valuation_layer(move)
            move.unlink_serial_number()
        return True


class stock_move_line(models.Model):
    _inherit = "stock.move.line"

    def unlink(self):
#        uom_precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
#        for move_line in self:
#            if move_line.product_id.type == 'product' and not move_line.location_id.should_bypass_reservation() and not float_is_zero(
#                    move_line.product_qty, precision_digits=uom_precision):
#                self.env['stock.quant']._update_reserved_quantity(move_line.product_id, move_line.location_id,
#                                                                  -move_line.product_qty, lot_id=move_line.lot_id,
#                                                                  package_id=move_line.package_id,
#                                                                  owner_id=move_line.owner_id, strict=True)
        return super(stock_move_line,self).unlink()

    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
