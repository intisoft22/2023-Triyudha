# -*- coding: utf-8 -*-

from odoo import models
from datetime import datetime

class RegisterPenjualanXlsx(models.AbstractModel):
    _name = 'report.sales_report.report_register_penjualan_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, purchase):
        bold = workbook.add_format({'bold': True})
        bold_border = workbook.add_format({'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center',})
        bold_center = workbook.add_format({'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center', 'font_color': 'blue'})
        date_style = workbook.add_format({'text_wrap': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': 'dd-mmm-yyyy'})
        money_format = workbook.add_format({'text_wrap': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': '#,##0.00'})
        int_format = workbook.add_format({'text_wrap': True,'align': 'right', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': '#,##0'})
        float_format = workbook.add_format({'text_wrap': True,'align': 'right', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': '#,##0.00'})
        money_format_bold = workbook.add_format({'text_wrap': True, 'num_format': '#,##0.00', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1})
        border = workbook.add_format({'left': 1, 'bottom': 1, 'right': 1, 'top': 1})

        for obj in purchase:
            sheet = workbook.add_worksheet('Register Penjualan')
            sheet.set_column('A:A', 20)
            sheet.set_column('B:B', 20)
            sheet.set_column('C:C', 20)
            sheet.set_column('D:D', 20)
            sheet.set_column('E:E', 20)
            sheet.set_column('F:F', 20)
            sheet.set_column('G:G', 20)
            sheet.set_column('H:H', 20)
            sheet.set_column('I:I', 20)
            sheet.set_column('J:J', 20)
            sheet.set_column('K:K', 20)
            sheet.set_column('L:L', 20)
            sheet.set_column('M:M', 20)
            sheet.set_column('N:N', 20)
            sheet.set_column('O:O', 20)
            sheet.set_column('P:P', 20)
            sheet.set_column('Q:Q', 20)

            row = 0
            col = 0
            col_tgl = col + 0
            col_cus = col + 1
            col_sj = col + 2
            col_faktur = col + 3
            col_type = col + 4
            col_type_2 = col + 5
            col_kode = col + 6
            col_name = col + 7
            col_berat = col + 8
            col_qty = col + 9
            col_berat_qty = col + 10
            col_harga = col + 11
            col_harga_per = col + 12
            col_jml = col + 13
            col_ppn_11 = col + 14
            col_pph_23 = col + 15
            col_total = col + 16

            sheet.write(row, col, 'PT. TRIYUDA TOPHERINDO NUSANTARA', bold)
            row += 1
            sheet.write(row, col, 'REGISTER PENJUALAN', bold)
            row += 1
            sheet.write(row, col, 'Bulan : ' + data['month'] + ' ' + data['year'], bold)

            row += 2
            sheet.write(row, col_tgl, 'TGL', bold_border)
            sheet.write(row, col_cus, 'CUSTOMER', bold_border)
            sheet.write(row, col_sj, 'NO SJ', bold_border)
            sheet.write(row, col_faktur, 'NO FAKTUR', bold_border)
            sheet.write(row, col_type, 'TYPE', bold_border)
            sheet.write(row, col_type_2, ' ', bold_border)
            sheet.write(row, col_kode, 'KODE STOCK', bold_border)
            sheet.write(row, col_name, 'NAME STOCK', bold_border)
            sheet.write(row, col_berat, 'BERAT', bold_border)
            sheet.write(row, col_qty, 'QTY', bold_border)
            sheet.write(row, col_berat_qty, 'TTL BERAT', bold_border)
            sheet.write(row, col_harga, 'HARGA xG', bold_border)
            sheet.write(row, col_harga_per, 'HARGA PER STG', bold_border)
            sheet.write(row, col_jml, 'JUMLAH', bold_border)
            sheet.write(row, col_ppn_11, 'PPN 11%', bold_border)
            sheet.write(row, col_pph_23, 'PPH 23', bold_border)
            sheet.write(row, col_total, 'TOTAL', bold_border)


