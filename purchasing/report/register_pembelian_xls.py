# -*- coding: utf-8 -*-

from odoo import models
from datetime import datetime

class RegisterPembelianXlsx(models.AbstractModel):
    _name = 'report.purchasing.report_register_pembelian_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, purchase):
        bold = workbook.add_format({'bold': True})
        bold_center = workbook.add_format({'bold': True, 'align': 'center'})
        date_style = workbook.add_format({'text_wrap': True, 'num_format': 'dd/mm/yyyy'})
        money_format = workbook.add_format({'text_wrap': True, 'num_format': '#,##0.00'})
        money_format_bold = workbook.add_format({'text_wrap': True, 'num_format': '#,##0.00', 'bold': True})

        for obj in purchase:
            sheet = workbook.add_worksheet('Register Pembelian')
            sheet.set_column('A:A', 15)
            sheet.set_column('B:B', 20)
            sheet.set_column('C:C', 20)
            sheet.set_column('D:D', 20)
            sheet.set_column('E:E', 30)
            sheet.set_column('F:F', 20)
            sheet.set_column('G:G', 20)
            sheet.set_column('H:H', 15)
            sheet.set_column('I:I', 15)
            sheet.set_column('J:J', 15)
            sheet.set_column('K:K', 15)
            sheet.set_column('L:L', 15)

            row = 0
            col = 0
            col_tgl = col + 0
            col_sup = col + 1
            col_fp = col + 2
            col_code = col + 3
            col_nama = col + 4
            col_jml_brg = col + 5
            col_harga = col + 6
            col_dpp = col + 7
            col_ppn = col + 8
            col_p23 = col + 9
            col_p22 = col + 10
            col_jml = col + 11

            sheet.write(row, col, 'PT. TRIYUDA TOPHERINDO NUSANTARA', bold)
            row += 1
            sheet.write(row, col, 'REGISTER PEMBELIAN', bold)
            row += 1
            sheet.write(row, col, 'Bulan : ' + data['month'] + ' ' + data['year'], bold)

            row += 2
            sheet.write(row, col_tgl, 'TGL', bold_center)
            sheet.write(row, col_sup, 'SUPPLIER', bold_center)
            sheet.write(row, col_fp, 'FAKTUR PAJAK', bold_center)
            sheet.write(row, col_code, 'KODE', bold_center)
            sheet.write(row, col_nama, 'NAMA BARANG', bold_center)
            sheet.write(row, col_jml_brg, 'JUMLAH BARANG', bold_center)
            sheet.write(row, col_harga, 'HARGA SATUAN', bold_center)
            sheet.write(row, col_dpp, 'DPP', bold_center)
            sheet.write(row, col_ppn, 'PPN', bold_center)
            sheet.write(row, col_p23, 'PPH 23', bold_center)
            sheet.write(row, col_p22, 'PPH 22', bold_center)
            sheet.write(row, col_jml, 'JUMLAH', bold_center)

            for x in data['vals']:
                for y in x:
                    row += 1
                    sheet.write(row, col_tgl, datetime.strptime(y['bill_date'], '%Y-%m-%d'), date_style)
                    sheet.write(row, col_sup, y['vendor'])
                    sheet.write(row, col_nama, y['nama_barang'])
                    sheet.write(row, col_jml_brg, y['quantity'])
                    sheet.write(row, col_fp, y['tax_number'])
                    sheet.write(row, col_harga, y['price_unit'], money_format)
                    sheet.write(row, col_code, y['coa'])
                    sheet.write(row, col_dpp, y['dpp'], money_format)
                    sheet.write(row, col_ppn, y['ppn'], money_format)
                    sheet.write(row, col_p23, y['pph23'], money_format)
                    sheet.write(row, col_p22, y['pph22'], money_format)
                    sheet.write(row, col_jml, y['jumlah'], money_format)

            if data['vals']:
                row += 2
                sheet.write(row, col_jml_brg, data['total_quantity'], bold)
                sheet.write(row, col_dpp, data['total_dpp'], money_format_bold)
                sheet.write(row, col_ppn, data['total_ppn'], money_format_bold)
                sheet.write(row, col_p23, data['total_pph23'], money_format_bold)
                sheet.write(row, col_p22, data['total_pph22'], money_format_bold)
                sheet.write(row, col_jml, data['total_jumlah'], money_format_bold)