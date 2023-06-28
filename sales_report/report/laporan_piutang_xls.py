# -*- coding: utf-8 -*-

from odoo import models
from datetime import datetime

class LaporanPiutangXlsx(models.AbstractModel):
    _name = 'report.sales_report.report_laporan_piutang_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, purchase):
        bold = workbook.add_format({'bold': True})
        bold_border = workbook.add_format({'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center', 'bg_color': '#ddc8ba'})
        date_style = workbook.add_format({'text_wrap': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': 'dd-mmm-yyyy'})
        money_format = workbook.add_format({'text_wrap': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': '#,##0.00'})
        int_format = workbook.add_format({'text_wrap': True,'align': 'right', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': '#,##0'})
        float_format = workbook.add_format({'text_wrap': True,'align': 'right', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': '#,##0.00'})
        money_format_bold = workbook.add_format({'text_wrap': True, 'num_format': '#,##0.00', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1})
        border = workbook.add_format({'left': 1, 'bottom': 1, 'right': 1, 'top': 1})
        header = workbook.add_format({'bold': True, 'align': 'center'})

        for obj in purchase:
            sheet = workbook.add_worksheet('Laporan Piutang')
            sheet.set_column('B:B', 20)
            sheet.set_column('C:C', 20)
            sheet.set_column('D:D', 30)
            sheet.set_column('E:E', 20)
            sheet.set_column('F:F', 20)

            row = 0
            col = 0
            col_no = col + 0
            col_cus = col + 1
            col_ambil = col + 2
            col_tempo = col + 3
            col_saldo = col + 4
            col_bulan = col + 5


            sheet.merge_range(row, col, row, col + 6, 'PIUTANG METAL PIPE & DATA PENGAMBILAN (OMZET) - ' + data['month'] + ' ' + data['year'] , header)

            row += 2
            sheet.write(row, col_no, 'No', bold_border)
            sheet.write(row, col_cus, 'CUSTOMER', bold_border)
            sheet.write(row, col_ambil, 'PENGAMBILAN', bold_border)
            sheet.write(row, col_tempo, 'PIUTANG JATUH TEMPO', bold_border)
            sheet.write(row, col_saldo, 'SALDO PIUTANG', bold_border)
            sheet.write(row, col_bulan, 'BULAN', bold_border)



