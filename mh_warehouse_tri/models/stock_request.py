from odoo import SUPERUSER_ID,api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare

from collections import defaultdict, namedtuple
from datetime import datetime,date
from lxml import etree

import time
import json
from odoo.tools.misc import clean_context, format_date, OrderedSet

class ProcurementException(Exception):
    """An exception raised by ProcurementGroup `run` containing all the faulty
    procurements.
    """
    def __init__(self, procurement_exceptions):
        """:param procurement_exceptions: a list of tuples containing the faulty
        procurement and their error messages
        :type procurement_exceptions: list
        """
        self.procurement_exceptions = procurement_exceptions


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    date_planned = fields.Date()

class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    initial = fields.Char('Initial')


class StockRequest(models.Model):
    _inherit = 'stock.request'
    categ_id = fields.Many2one('product.category', string='Product Category')

    product_categ_id = fields.Many2one('product.category', string='Category', )

    product_id_domain = fields.Char(
        compute="_compute_product_id_domain",
        readonly=True,
        store=False,
    )
    category = fields.Selection([
        ('warehouse', 'Inter Warehouse'),
        ('location', 'Inter Location'),
    ], string='Category')

    note = fields.Text('Note')

    @api.depends('categ_id')
    def _compute_product_id_domain(self):
        for rec in self:
            if rec.categ_id:
                Product = self.env['product.product']
                categ_products = Product.search([('categ_id', 'child_of', rec.categ_id.id)])
                # print(categ_products)
                # print("===============================")
                product_array = []
                for x in categ_products:
                    product_array.append(x.id)

                # return {'domain': {'product_id': [('id', 'in', product_array)]}}
                # print(product_array)
                rec.product_id_domain = json.dumps(
                    [('id', 'in', product_array)]
                )
            else:
                # return {'domain': {'product_id': [('id', '=', 0)]}}
                rec.product_id_domain = json.dumps(
                    [('id', '=', 0)]
                )

    def _action_launch_procurement_rule(self):
        """
        Launch procurement group run method with required/custom
        fields genrated by a
        stock request. procurement group will launch '_run_move',
        '_run_buy' or '_run_manufacture'
        depending on the stock request product rule.
        """
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        errors = []
        # print("action confirm")
        for request in self:
            if request._skip_procurement():
                continue
            qty = 0.0
            for move in request.move_ids.filtered(
                    lambda r: r.state != 'cancel'):
                qty += move.product_qty

            if float_compare(qty, request.product_qty,
                             precision_digits=precision) >= 0:
                continue

            values = request._prepare_procurement_values(
                group_id=request.procurement_group_id)

            values.update({
                'ket_req': request.note,
                'split': True
            })
            # print("===================PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP=")
            # print(values)
            try:
                # We launch with sudo because potentially we could create
                # objects that the user is not authorized to create, such
                # as PO.
                procurements = []
                procurements.append(
                    self.env["procurement.group"].Procurement(
                        request.product_id, request.product_uom_qty,
                        request.product_uom_id,
                        request.location_id, request.name,
                        request.name,
                        self.env.company, values
                    )
                )
                print(procurements)
                self.env["procurement.group"].sudo().run(procurements)

                picking = self.env['stock.picking'].search([
                    ('group_id', '=', request.procurement_group_id.id)])
                if picking:
                    for p in picking:
                        p.write({
                            'origin': request.order_id.name,
                        })
                        # for m in p.move_ids_without_package:
                        #     if m.product_id.id == request.product_id.id:
                        #         m.note = request.note



            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True

class StockRequestOrder(models.Model):
    _inherit = 'stock.request.order'

    route_id = fields.Many2one('stock.location.route', string='Route', states={'draft': [('readonly', False)]},
                               readonly=True, required=True)

    warehouse_id = fields.Many2one(
        'stock.warehouse', 'Warehouse', readonly=True,
        ondelete="cascade", required=True,
        states={'draft': [('readonly', False)]}, domain="[('name','=','-')]")

    location_id = fields.Many2one(
        'stock.location', 'Location', readonly=True,
        domain=[('usage', 'in', ['internal', 'transit'])],
        ondelete="cascade", required=True,
    )

    category = fields.Selection([
        ('warehouse', 'Inter Warehouse'),
        ('location', 'Inter Location'),
    ], string='Category')
    categ_id = fields.Many2one('product.category', string='Produk Kategori', states={'draft': [('readonly', False)]},
                               readonly=True, required=True, )
    type_id = fields.Many2one('stock.request.type', string='Tipe Serah Terima',
                              states={'draft': [('readonly', False)]},
                              readonly=True, required=True)
    src_warehouse_id = fields.Many2one(
        'stock.warehouse', 'Source Warehouse', readonly=True,
        ondelete="cascade",
        states={'draft': [('readonly', False)]})
    src_location_id = fields.Many2one(
        'stock.location', 'Source Location', readonly=True,
        domain=[('usage', 'in', ['internal', 'transit'])],
        ondelete="cascade",
        states={'draft': [('readonly', False)]},
    )

    note = fields.Text('Note')

    send_date = fields.Datetime(
        'Send Date', index=True,
        readonly=True,
    )
    receive_date = fields.Datetime(
        'Receive Date', index=True,
        readonly=True,
    )
    check_user = fields.Boolean(
        string="Check User", store=True,
        compute="_get_checkuser"
    )
    check_user2 = fields.Boolean(
        string="Check User",
        compute="_get_checkuser"
    )
    picking_count = fields.Integer(string='Delivery Orders',
                                   compute='_compute_picking_ids',
                                   readonly=True,
                                   )
    @api.model
    def create(self, vals):
        upd_vals = vals.copy()
        location = False

        route_id = upd_vals.get('route_id')
        route = self.env['stock.location.route'].search([
            ('id', '=', route_id)])
        koderoute = route.initial
        for r in route.rule_ids:
            if r.action == 'pull':
                location = r.location_id.id
        upd_vals['location_id'] = location

        bulanskrng = datetime.now().month
        tahunskrng = datetime.strptime(str(datetime.now().year), '%Y').strftime('%Y')
        # print(upd_vals.get('create_date'))

        # today = datetime.strptime(str(upd_vals.get('create_date')), '%Y-%m-%d %H:%M:%S')
        today = datetime.strptime(str(upd_vals.get('expected_date')), '%Y-%m-%d %H:%M:%S')
        dateawal = datetime(today.year - 1, 12, 31, 17, 00, 00)
        dateakhir = datetime(today.year, 12, 31, 16, 59, 59)
        sro_ids = self.env['stock.request.order'].search(
            [('route_id', '=', route_id), ('expected_date', '<=', str(dateakhir)),
             ('expected_date', '>=', str(dateawal))],
        )
        last_sqi = 1
        if sro_ids:
            numbernow = 0
            for sro in sro_ids:

                lastnow = sro[0].name.split('/')
                if len(lastnow) == 4:
                    if int(lastnow[3]) > numbernow:
                        numbernow = int(lastnow[3])

            last_sqi = numbernow + 1

        seq = 'SRO/' + str(tahunskrng).zfill(4) + "/" + str(koderoute) + "/" + str(last_sqi).zfill(4)

        upd_vals['name'] = seq

        return super().create(upd_vals)

    def write(self, values):

        upd_vals = values.copy()
        if self.state == 'draft':
            if self.create_uid.id != self.env.uid:
                raise UserError(_("You are not the creator of this document"))
        if upd_vals.get('route_id'):
            location = False

            route_id = upd_vals.get('route_id')
            route = self.env['stock.location.route'].search([
                ('id', '=', route_id)])

            koderoute = route.initial
            for r in route.rule_ids:
                if r.action == 'pull':
                    location = r.location_id.id

            upd_vals['location_id'] = location

            bulanskrng = datetime.now().month
            tahunskrng = datetime.strptime(str(datetime.now().year), '%Y').strftime('%Y')
            # print(upd_vals.get('create_date'))

            # today = datetime.strptime(str(upd_vals.get('create_date')), '%Y-%m-%d %H:%M:%S')
            today = datetime.today()
            dateawal = datetime(today.year - 1, 12, 31, 17, 00, 00)
            dateakhir = datetime(today.year, 12, 31, 16, 59, 59)
            sro_ids = self.env['stock.request.order'].search(
                [('route_id', '=', route_id), ('expected_date', '<=', str(dateakhir)),
                 ('expected_date', '>=', str(dateawal))],
            )

            lastnow = self.name.split('/')
            if len(lastnow) == 3:

                seq = lastnow[0] + '/' + lastnow[1] + "/" + str(koderoute) + "/" + lastnow[3]
            else:
                last_sqi = 1
                if sro_ids:
                    numbernow = 0
                    for sro in sro_ids:

                        lastnow = sro[0].name.split('/')
                        if len(lastnow) == 4:
                            if int(lastnow[3]) > numbernow:
                                numbernow = int(lastnow[3])

                    last_sqi = numbernow + 1

                seq = 'SRO/' + str(tahunskrng).zfill(4) + "/" + str(koderoute) + "/" + str(last_sqi).zfill(4)

            upd_vals['name'] = seq
        res = super().write(upd_vals)
        return res

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            # search with sudo because the user may not have permissions
            loc_wh = self.location_id.sudo().get_warehouse()
            if self.warehouse_id != loc_wh:
                self.location_id = False
                self.with_context(no_change_childs=True).onchange_location_id()
            if self.warehouse_id.sudo().company_id != self.company_id:
                self.company_id = self.warehouse_id.company_id
                self.with_context(no_change_childs=True).onchange_company_id()
        self.change_childs()

    @api.depends('procurement_group_id')
    def _compute_picking_ids(self):
        for record in self:
            if record.procurement_group_id:
                if record.state in ['open','done']:
                    picking = self.env['stock.picking'].search([
                        ('group_id', '=', record.procurement_group_id.id)])
                    picking_array = []
                    if picking:
                        for p in picking:
                            picking_array.append(p.id)
                    record.picking_count = len(picking_array)
                    record.picking_ids = False
                else:
                    record.picking_count = 0
                    record.picking_ids = False
            else:

                record.picking_count = 0
                record.picking_ids = False



    def action_view_transfer(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        picking = self.env['stock.picking'].search([
            ('group_id', '=', self.procurement_group_id.id)])
        picking_array = []
        if picking:
            for p in picking:
                picking_array.append(p.id)
        if len(picking_array) > 1:
            action['domain'] = [('id', 'in', picking_array)]
        elif picking_array:
            action['views'] = [
                (self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = picking_array[0]
        return action

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        # print(res)
        # print("=================ad")
        if self.env.user.company_id:
            warehouse = self.env['stock.warehouse'].search(
                [('company_id', '=', self.env.user.company_id.id)], limit=1)
            if warehouse:
                res['warehouse_id'] = warehouse.id
                res['location_id'] = warehouse.lot_stock_id.id
        # res['warehouse_id'] = False
        # res['location_id'] = False
        # print(res)
        # print("=================adaa")
        return res

    @api.depends('create_uid', 'src_warehouse_id', 'warehouse_id')
    def _get_checkuser(self):
        for x in self:

            x.check_user2 = False
            if x.state == "draft":
                if x.create_uid.id == self.env.user.id:
                    x.check_user2 = True
            if x.state == "submitted":

                if self.env.user.has_group('mh_warehouse_tri.group_confirm_sr'):
                    x.check_user2 = True

    @api.onchange('company_id')
    def onchange_company_id(self):

        return {
            'domain': {
                'warehouse_id': [('company_id', '=', self.company_id.id)]}}

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        self.stock_request_ids = False

    @api.onchange('route_id')
    def onchange_route_id(self):
        for line in self.stock_request_ids:
            line.route_id = self.route_id
        location = False
        tolocation = False
        warehouse = False
        for r in self.route_id.rule_ids:
            if r.action == 'pull':
                location = r.location_src_id.id
                warehouse = r.picking_type_id.warehouse_id.id
                break

        for r in self.route_id.rule_ids:
            if r.action == 'pull':
                tolocation = r.location_id.id
        # print("route_d")
        # print(location)
        # print(warehouse)
        # print("===========")
        self.location_id = tolocation
        self.src_location_id = location
        self.src_warehouse_id = warehouse

    @api.onchange('type_id', 'warehouse_id')
    def onchange_to_route(self):
        self.category = self.type_id.category
        self.route_id = False
        if self.type_id:

            categ_ids = []
            for categ in self.type_id.categ_id:
                categ_ids.append(categ.id)
            if len(categ_ids) > 0:
                self.categ_id = categ_ids[0]


            if self.warehouse_id:

                route_ids = []
                for route in self.type_id.route_id:
                    warehouseroute = []
                    for x in route.warehouse_ids:
                        warehouseroute.append(x.id)
                    if self.warehouse_id and self.warehouse_id.id in warehouseroute:
                        route_ids.append(route.id)

                self.route_id = route_ids[0]
                return {'domain': {'route_id': [('id', 'in', route_ids)], 'warehouse_id': [('company_id', '=', self.company_id.id)],
                                   'categ_id': [('id', 'in', categ_ids)]}}
            else:
                return {'domain': {'warehouse_id': [('company_id', '=', self.company_id.id)], 'categ_id': [('id', 'in', categ_ids)]}}

        else:
            self.categ_id = False
            return {'domain': {'route_id': [], 'categ_id': []}}

    def action_confirm(self):

        for sro in self:
            vals = {}
            proc_group_obj = self.env['procurement.group']
            vals['date_planned'] = self.expected_date
            id_group = proc_group_obj.create(
                vals)
            # print(id_group)
            order_proc_group_to_use = \
                sro.procurement_group_id = id_group.id
            print(id_group)
            sro.procurement_group_id=order_proc_group_to_use
            print("sro.procurement_group_id")
            print(sro.procurement_group_id)
            if sro.procurement_group_id:
                for x in sro.stock_request_ids:
                    x.procurement_group_id = sro.procurement_group_id.id
            res = super().action_confirm()
            return res

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id,
                               values):
        result = super(StockRule, self)._get_stock_move_values(
            product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
        if values.get('ket_req', False):
            result['note'] = values.get('ket_req', False)
        if values.get('split', False):
            result['split'] = values.get('split', False)

        return result

    @api.model
    def _run_pull(self, procurements):
        moves_values_by_company = defaultdict(list)
        mtso_products_by_locations = defaultdict(list)

        # To handle the `mts_else_mto` procure method, we do a preliminary loop to
        # isolate the products we would need to read the forecasted quantity,
        # in order to to batch the read. We also make a sanitary check on the
        # `location_src_id` field.
        for procurement, rule in procurements:
            if not rule.location_src_id:
                msg = _('No source location defined on stock rule: %s!') % (rule.name, )
                raise ProcurementException([(procurement, msg)])

            if rule.procure_method == 'mts_else_mto':
                mtso_products_by_locations[rule.location_src_id].append(procurement.product_id.id)

        # Get the forecasted quantity for the `mts_else_mto` procurement.
        forecasted_qties_by_loc = {}
        for location, product_ids in mtso_products_by_locations.items():
            products = self.env['product.product'].browse(product_ids).with_context(location=location.id)
            forecasted_qties_by_loc[location] = {product.id: product.free_qty for product in products}

        # Prepare the move values, adapt the `procure_method` if needed.
        for procurement, rule in procurements:
            procure_method = rule.procure_method
            if rule.procure_method == 'mts_else_mto':
                qty_needed = procurement.product_uom._compute_quantity(procurement.product_qty, procurement.product_id.uom_id)
                qty_available = forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id]
                if float_compare(qty_needed, qty_available, precision_rounding=procurement.product_id.uom_id.rounding) <= 0:
                    procure_method = 'make_to_stock'
                    forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id] -= qty_needed
                else:
                    procure_method = 'make_to_order'

            move_values = rule._get_stock_move_values(*procurement)
            print(move_values)
            move_values['procure_method'] = procure_method
            moves_values_by_company[procurement.company_id.id].append(move_values)

        for company_id, moves_values in moves_values_by_company.items():
            # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            moves = self.env['stock.move'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(moves_values)
            # Since action_confirm launch following procurement_group we should activate it.
            print(moves_values)
            if not moves_values[0].get('split'):
                # print("TEs")
                moves._action_confirm()

            else:
                # print("TE22s")
                moves._action_confirm(merge=False)
        return True
class StockMove(models.Model):
    _inherit = 'stock.move'

    note = fields.Text('Note')
    split = fields.Boolean('Split')

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        for x in self:
            # print(x.move_dest_ids)

            if x.allocation_ids.sudo():
                qty_done = x.product_uom._compute_quantity(
                    x.quantity_done, x.product_id.uom_id)
                # print("+++++++++++++++++++++++++++")
                # print(qty_done)
                # We do sudo because potentially the user that completes the move
                #  may not have permissions for stock.request.
                to_allocate_qty = qty_done
                for allocation in x.allocation_ids.sudo():
                    allocation.allocated_product_qty += to_allocate_qty
                self.mapped('allocation_ids.stock_request_id').check_done()

            if x.move_dest_ids.sudo():
                for md in x.move_dest_ids:
                    if md.stock_request_ids:
                        # print(md.product_id.name)
                        for srq in md.stock_request_ids:
                            # print(srq.order_id.name)
                            srq.order_id.send_date = x.date
            else:
                if x.move_orig_ids:
                    if x.stock_request_ids:
                        x.stock_request_ids.order_id.receive_date = x.date
                else:
                    if x.stock_request_ids:
                        x.stock_request_ids.order_id.send_date = x.date
                        x.stock_request_ids.order_id.receive_date = x.date
        return res

    def _action_cancel(self):
        res = super()._action_cancel()
        # print("==================== cancel")
        self.mapped('allocation_ids.stock_request_id').check_done()
        return res

    def _action_confirm(self, merge=True, merge_into=False):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        :param: merge: According to this boolean, a newly confirmed move will be merged
        in another move of the same picking sharing its characteristics.
        """
        move_create_proc = self.env['stock.move']
        move_to_confirm = self.env['stock.move']
        move_waiting = self.env['stock.move']

        to_assign = {}
        split = False
        note = ""
        for move in self:
            # if the move is preceeded, then it's waiting (if preceeding move is done, then action_assign has been called already and its state is already available)
            if move.move_orig_ids:
                move_waiting |= move
            else:
                if move.procure_method == 'make_to_order':
                    move_create_proc |= move
                else:
                    move_to_confirm |= move
            if move._should_be_assigned():
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                if key not in to_assign:
                    to_assign[key] = self.env['stock.move']
                to_assign[key] |= move
            if move.split:
                split = True
            if move.note:
                note = move.note

        # print(move_create_proc)

        # create procurements for make to order moves

        procurement_requests = []
        for move in move_create_proc:
            values = move._prepare_procurement_values()
            values.update({
                'ket_req': note})
            if split:
                values.update({
                    'split': True})

            # print("=======================================")
            origin = (move.group_id and move.group_id.name or (move.origin or move.picking_id.name or "/"))
            procurement_requests.append(self.env['procurement.group'].Procurement(
                move.product_id, move.product_uom_qty, move.product_uom,
                move.location_id, move.rule_id and move.rule_id.name or "/",
                origin, move.company_id, values))
        self.env['procurement.group'].run(procurement_requests,
                                          raise_user_error=not self.env.context.get('from_orderpoint'))


        move_to_confirm.write({'state': 'confirmed'})
        (move_waiting | move_create_proc).write({'state': 'waiting'})

        # assign picking in batch for all confirmed move that share the same details
        for moves in to_assign.values():
            moves.with_context(clean_context(moves.env.context))._assign_picking()
        self._push_apply()
        self._check_company()
        moves = self
        if merge:
            moves = self._merge_moves(merge_into=merge_into)
        # call `_action_assign` on every confirmed move which location_id bypasses the reservation
        moves.filtered(lambda move: not move.picking_id.immediate_transfer and move._should_bypass_reservation() and move.state == 'confirmed')._action_assign()
        return moves

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_assign(self):
        """If any stock move is to be invoiced, picking status is updated"""
        # for move in self.move_ids_without_package:
        #     location = self.location_id.id
        #     qty_onhand = move.product_id.with_context(location=location)._compute_quantities_dict(
        #         self._context.get('lot_id'),
        #         self._context.get('owner_id'),
        #         self._context.get('package_id'),
        #         self._context.get('from_date'),
        #         self._context.get('to_date'))
        #     # print(qty_onhand)
        #     # print("teeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        #     move.onhand_qty = qty_onhand[move.product_id.id]['qty_available']

        res = super(StockPicking, self).action_assign()
        # print("Tesss")
        for x in self:

            for move in x.move_ids_without_package:
                for moveline in move.move_line_ids:
                    moveline.qty_done = moveline.product_uom_qty
        return res