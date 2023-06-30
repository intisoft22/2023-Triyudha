# -*- coding: utf-8 -*-

from odoo import models
from datetime import date, datetime


class KartuStockXlsx(models.AbstractModel):
    _name = 'report.warehouse_inventory_report.report_kartu_stock_xls'
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, stock):
        today = date.today()
        dt = 'Tanggal Print : ' + str(today.strftime("%Y-%m-%d"))
        bold = workbook.add_format({'bold': True, 'border': 1})
        bold_center = workbook.add_format({'bold': True, 'align': 'center', 'border': 1, 'bg_color': 'yellow'})
        format_data = workbook.add_format({'border': 1})

        for i in data['product']:
            row = 11

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

            sheet.merge_range(0, 0, 0, 5, 'PT. TRIYUDA TOPHERINDO NUSANTARA', bold_center)
            sheet.merge_range(1, 0, 1, 5, 'NAMA BARANG : [' + i[0] + '] ' + i[1], format_data)
            sheet.merge_range(2, 0, 2, 5, 'SATUAN : ' + i[2], format_data)
            sheet.merge_range(3, 0, 3, 5, 'NO KARTU : ', format_data)
            sheet.merge_range(4, 0, 4, 5, dt, format_data)
            sheet.merge_range(5, 0, 5, 5, 'DARI TANGGAL : ' + str(data['start']), format_data)
            sheet.merge_range(6, 0, 6, 5, 'SAMPAI TANGGAL : ' + str(data['end']), format_data)

            sheet.write(9, 0, 'TGL', bold_center)
            sheet.write(9, 1, 'NO BUKTI', bold_center)
            sheet.write(9, 2, 'KETERANGAN', bold_center)
            sheet.write(9, 3, 'MASUK', bold_center)
            sheet.write(9, 4, 'KELUAR', bold_center)
            sheet.write(9, 5, 'SISA', bold_center)

            sheet.write(10, 0, '', format_data)
            sheet.write(10, 1, '', bold)
            sheet.write(10, 2, 'saldo awal', format_data)
            sheet.write(10, 3, '', format_data)
            sheet.write(10, 4, '', format_data)
            sheet.write(10, 5, 'str(i[3])', format_data)

            saldo = i[3]
            for data_stock in i[4]:
                sheet.write(row, 0, data_stock[0], format_data)
                sheet.write(row, 1, data_stock[1], format_data)
                if data_stock[2] != 0:
                    sheet.write(row, 2, data_stock[2], format_data)
                else:
                    sheet.write(row, 2, '', format_data)
                if data_stock[3] != 0:
                    sheet.write(row, 3, data_stock[3], format_data)
                    saldo = saldo + data_stock[3]
                else:
                    sheet.write(row, 3, '', format_data)
                if data_stock[4] != 0:
                    sheet.write(row, 4, data_stock[4], format_data)
                    saldo = saldo - data_stock[4]
                else:
                    sheet.write(row, 4, '', format_data)
                sheet.write(row, 5, saldo, format_data)
                row += 1

