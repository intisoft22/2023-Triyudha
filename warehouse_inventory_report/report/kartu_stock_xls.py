# -*- coding: utf-8 -*-

from odoo import models
from datetime import datetime

class KartuStockXlsx(models.AbstractModel):
    _name = 'report.warehouse_inventory_report.report_kartu_stock_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, stock):
        bold = workbook.add_format({'bold': True})
        bold_center = workbook.add_format({'bold': True, 'align': 'center'})
        sheet = workbook.add_worksheet('Kartu Stock')
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 30)
        sheet.set_column('K:K', 30)
        sheet.set_column('L:L', 30)

        sheet.write(0, 0, 'PT. TRIYUDA TOPHERINDO NUSANTARA', bold)
        sheet.write(1, 0, 'NAMA BARANG: ', bold)
        sheet.write(2, 0, 'SATUAN: ', bold)
        sheet.write(3, 0, 'NO KARTU: ', bold)

        sheet.write(5, 0, 'TGL', bold_center)
        sheet.write(5, 1, 'NO BUKTI', bold_center)
        sheet.write(5, 2, 'KETERANGAN', bold_center)
        sheet.write(5, 3, 'MASUK', bold_center)
        sheet.write(5, 4, 'KELUAR', bold_center)
        sheet.write(5, 5, 'SISA', bold_center)
