# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import timedelta, date
import dateutil.parser

class KartuStockWizard(models.TransientModel):
    _name = "kartu.stock.wizard"
    _description = "Kartu Stock Wizard"

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    kategori_produk = fields.Many2one('product.category', string='Kategori Produk', domain="[('parent_id', '=', False)]", required=True)
    produk = fields.Many2many('product.product', string="Produk", required=False, invisible=True)
    all_produk = fields.Boolean(string="All Produk", default=True, )



    @api.onchange("kategori_produk")
    def _onchange_kategori_produk(self):
        for rec in self:
            return {'domain': {'produk': [('categ_id', '=', rec.kategori_produk.name)]}, }


    def action_print_kartu(self):
        nama_product = []
        location_name = []
        date_range = []
        produk = self.env['product.product'].search([
            ('categ_id', '=', self.kategori_produk.name)
        ])
        stock_location_name = self.env['stock.location'].search([
            ('categ_id', '=', self.kategori_produk.name)
        ])
        for rec_stock in stock_location_name:
            location_name.append(rec_stock['complete_name'])


        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days) + 1):
                yield start_date + timedelta(n)

        for single_date in daterange(self.date_from, self.date_to):
            date_range.append(single_date)





        if self.all_produk == True:
            saldo_awal = 0
            stock_move_range = []

            for i in produk:
                # Mencari Saldo Awal
                stock_move = self.env['stock.move'].search([
                    ('state', '=', 'done'),
                    ('product_id', 'like', str(i['name']))
                ])
                for j in stock_move:
                    if dateutil.parser.parse(str(j['date'])).date() < self.date_from:
                        if j['location_id'].complete_name in location_name:
                            print(j['product_uom_qty'], "KELUAR")
                            saldo_awal = saldo_awal - (j['product_uom_qty'])
                        if j['location_dest_id'].complete_name in location_name:
                            print(j['product_uom_qty'], "MASUK")
                            saldo_awal = saldo_awal + (j['product_uom_qty'])

                # Mencari Data Berdasarkan Range
                stock_move_env = self.env['stock.move'].search([
                    ('state', '=', 'done'),
                    ('product_id', 'like', str(i['name']))
                ])
                for j in stock_move_env:
                    print(dateutil.parser.parse(str(j['date'])).date())
                    if dateutil.parser.parse(str(j['date'])).date() in date_range:
                        if j['location_id'].complete_name in location_name:
                            stock_move_range.append([dateutil.parser.parse(str(j['date'])).date(), j['picking_id'].name, j['picking_id'].note, j['product_uom_qty'], 0])
                        if j['location_dest_id'].complete_name in location_name:
                            stock_move_range.append([dateutil.parser.parse(str(j['date'])).date(), j['picking_id'].name, j['picking_id'].note, 0, j['product_uom_qty']])

                nama_product.append([str(i['default_code']), str(i['name']), str(i['uom_id'].name), saldo_awal, stock_move_range])
                saldo_awal = 0

                stock_move_range = []


        else:
            saldo_awal = 0
            stock_move_range = []

            for i in self.produk:
                # Mencari Saldo Awal
                stock_move = self.env['stock.move'].search([
                    ('state', '=', 'done'),
                    ('product_id', 'like', str(i['name']))
                ])
                for j in stock_move:
                    if dateutil.parser.parse(str(j['date'])).date() < self.date_from:
                        if j['location_id'].complete_name in location_name:
                            print(j['product_uom_qty'], "KELUAR")
                            saldo_awal = saldo_awal - (j['product_uom_qty'])
                        if j['location_dest_id'].complete_name in location_name:
                            print(j['product_uom_qty'], "MASUK")
                            saldo_awal = saldo_awal + (j['product_uom_qty'])

                # Mencari Data Berdasarkan Range
                stock_move_env = self.env['stock.move'].search([
                    ('state', '=', 'done'),
                    ('product_id', 'like', str(i['name']))
                ])
                for j in stock_move_env:
                    print(dateutil.parser.parse(str(j['date'])).date())
                    if dateutil.parser.parse(str(j['date'])).date() in date_range:
                        if j['location_id'].complete_name in location_name:
                            stock_move_range.append([dateutil.parser.parse(str(j['date'])).date(), j['picking_id'].name,
                                                     j['picking_id'].note, j['product_uom_qty'], 0])
                        if j['location_dest_id'].complete_name in location_name:
                            stock_move_range.append([dateutil.parser.parse(str(j['date'])).date(), j['picking_id'].name,
                                                     j['picking_id'].note, 0, j['product_uom_qty']])

                nama_product.append(
                    [str(i['default_code']), str(i['name']), str(i['uom_id'].name), saldo_awal, stock_move_range])
                saldo_awal = 0

                stock_move_range = []


        data = {
            'product': nama_product,
            'start': self.date_from,
            'end': self.date_to
                }

        return self.env.ref('warehouse_inventory_report.report_kartu_stock_xlsx').report_action(self, data=data)


