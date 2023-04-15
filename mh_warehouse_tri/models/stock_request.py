from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare

from datetime import datetime,date
from lxml import etree

import time
import json


class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    initial = fields.Char('Initial')

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
                return {'domain': {'route_id': [('id', 'in', route_ids)], 'warehouse_id': [('company_id', '=', self.company_id.id)],
                                   'categ_id': [('id', 'in', categ_ids)]}}
            else:
                return {'domain': {'warehouse_id': [('company_id', '=', self.company_id.id)], 'categ_id': [('id', 'in', categ_ids)]}}

        else:
            self.categ_id = False
            return {'domain': {'route_id': [], 'categ_id': []}}


