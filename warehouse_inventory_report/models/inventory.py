# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Inventory(models.Model):
    _inherit = "stock.picking"

    # Nomor stock picking
    no = fields.Char(string='stock_picking_name', required=True)

    # source document
    src = fields.Char(string='stock_picking_origin', required=True)

    # Merge String
    nomor = str(no) + "-" + str(src)

    gudang_asal = fields.Char(string='stock_picking_id_name', required=True)


    gudang_tujuan = fields.Char(string='stock_picking_location_dest_id_name', required=True)


    kode_produk = fields.Char(string='stock_move.product_id.default_code', required=True)

    nama_produk = fields.Char(string='stock_move.product_id.name', required=True)

    qty = fields.Char(string='stock_move.qty_done', required=True)

    uom = fields.Char(string='stock_move.product_uom.name', required=True)

    keterangan = fields.Char(string='stock_picking.note', required=True)

    tgl = fields.Char(string='stock_picking_origin', required=True)
