# -*- coding: utf-8 -*-

from odoo import api, fields, models

class KartuStockWizard(models.TransientModel):
    _name = "kartu.stock.wizard"
    _description = "Kartu Stock Wizard"

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    kategori_produk = fields.Char(string='Kategori Produk', required=True)
    produk = fields.Char(string="Produk", required=False, invisible=True)
    all_produk = fields.Boolean(string="All Produk", default=True, )



    def action_print_kartu(self):


        data = {}

        return self.env.ref('warehouse_inventory_report.report_kartu_stock_xlsx').report_action(self, data=data)


