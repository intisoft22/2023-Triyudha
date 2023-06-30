# -*- coding: utf-8 -*-

from odoo import models
from datetime import datetime

class FakturPenjualanXlsx(models.AbstractModel):
    _name = 'report.sales_report.report_faktur_penjualan_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, purchase):
        bold = workbook.add_format({'bold': True})
        bold_border = workbook.add_format({'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1,})
        bold_center = workbook.add_format({'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center', 'font_color': 'blue'})
        header = workbook.add_format({'bold': True, 'align': 'center'})
        header_red = workbook.add_format({'font_color': 'red', 'font_size': 15, 'bold': True, 'align': 'center'})
        date_style = workbook.add_format({'text_wrap': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': 'dd-mmm-yyyy'})
        money_format = workbook.add_format({'text_wrap': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': '#,##0.00'})
        int_format = workbook.add_format({'text_wrap': True,'align': 'right', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': '#,##0'})
        float_format = workbook.add_format({'text_wrap': True,'align': 'right', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': '#,##0.00'})
        money_format_bold = workbook.add_format({'text_wrap': True, 'num_format': '#,##0.00', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1})
        border = workbook.add_format({'left': 1, 'bottom': 1, 'right': 1, 'top': 1})

        for obj in purchase:
            sheet = workbook.add_worksheet('Faktur Penjualan')
            sheet.set_column('A:A', 20)
            sheet.set_column('B:B', 20)
            sheet.set_column('C:C', 20)
            sheet.set_column('D:D', 20)
            sheet.set_column('E:E', 20)
            sheet.set_column('F:F', 20)
            sheet.set_column('G:G', 20)

            row = 0
            col = 0

            col_no_faktur = col + 0
            col_tgl_faktur = col + 1
            col_no_pel = col + 2
            col_nama_pel = col + 3
            col_nilai_faktur = col + 4
            col_terutang = col + 5
            col_keterangan = col + 6

            sheet.merge_range(row, col, row, col + 6, 'PT. TRIYUDA TOPHERINDO NUSANTARA', header)
            row += 1
            sheet.merge_range(row, col, row, col + 6, 'Daftar Faktur Penjualan', header_red)
            row += 1
            sheet.merge_range(row, col, row, col + 6, 'Dari ' + data['date_from'] + ' Ke ' + data['date_to'], header)

            row += 2
            sheet.write(row, col_no_faktur, 'No. Faktur', bold_center)
            sheet.write(row, col_tgl_faktur, 'Tgl Faktur', bold_center)
            sheet.write(row, col_no_pel, 'No. Pelanggan', bold_center)
            sheet.write(row, col_nama_pel, 'Nama Pelanggan', bold_center)
            sheet.write(row, col_nilai_faktur, 'Nilai Faktur', bold_center)
            sheet.write(row, col_terutang, 'Terutang', bold_center)
            sheet.write(row, col_keterangan, 'Keterangan', bold_center)

