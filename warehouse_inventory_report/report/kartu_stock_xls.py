# -*- coding: utf-8 -*-

from odoo import models
from datetime import date

class KartuStockXlsx(models.AbstractModel):
    _name = 'report.warehouse_inventory_report.report_kartu_stock_xls'
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, stock):
        today = date.today()
        dt = 'Tanggal Print : ' + str(today.strftime("%d %B %Y"))
        bold = workbook.add_format({'bold': True, 'border': 2})
        bold_bg = workbook.add_format({'bold': True, 'border': 1, 'bg_color': 'yellow'})
        bold_center = workbook.add_format({'bold': True, 'align': 'center', 'border': 2, 'bg_color': 'yellow'})

        for i in data['product']:
            row = 9
            saldo = 0
            sheet = workbook.add_worksheet(i[1])
            sheet.set_column('A:A', 15)
            sheet.set_column('B:B', 45)
            sheet.set_column('C:C', 45)
            sheet.set_column('D:D', 15)
            sheet.set_column('E:E', 15)
            sheet.set_column('F:F', 15)
            sheet.set_column('G:G', 15)
            sheet.set_column('H:H', 15)
            sheet.set_column('I:I', 15)
            sheet.set_column('J:J', 30)
            sheet.set_column('K:K', 30)
            sheet.set_column('L:L', 30)

            sheet.merge_range(0, 0, 0, 5, 'PT. TRIYUDA TOPHERINDO NUSANTARA', bold_bg)
            sheet.merge_range(1, 0, 1, 5, 'NAMA BARANG : [' + i[0] + '] ' + i[1], bold)
            sheet.merge_range(2, 0, 2, 5, 'SATUAN : ' + i[2], bold)
            sheet.merge_range(3, 0, 3, 5, 'NO KARTU : ', bold)
            sheet.merge_range(4, 0, 4, 5, dt, bold)

            sheet.write(7, 0, 'TGL', bold_center)
            sheet.write(7, 1, 'NO BUKTI', bold_center)
            sheet.write(7, 2, 'KETERANGAN', bold_center)
            sheet.write(7, 3, 'MASUK', bold_center)
            sheet.write(7, 4, 'KELUAR', bold_center)
            sheet.write(7, 5, 'SISA', bold_center)

            sheet.write(8, 0, '', bold)
            sheet.write(8, 1, '', bold)
            sheet.write(8, 2, 'saldo awal = ' + str(i[3]), bold)
            sheet.write(8, 3, '', bold)
            sheet.write(8, 4, '', bold)
            sheet.write(8, 5, '', bold)

            saldo = i[3]
            for data_stock in i[4]:
                sheet.write(row, 0, data_stock[0], bold)
                sheet.write(row, 1, data_stock[1], bold)
                sheet.write(row, 2, data_stock[2], bold)
                if data_stock[3] != 0:
                    sheet.write(row, 3, data_stock[3], bold)
                    saldo = saldo + data_stock[3]
                else:
                    sheet.write(row, 3, '', bold)
                if data_stock[4] != 0:
                    sheet.write(row, 4, data_stock[4], bold)
                    saldo = saldo - data_stock[4]
                else:
                    sheet.write(row, 4, '', bold)
                sheet.write(row, 5, saldo, bold)
                row += 1

