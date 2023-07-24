# -*- coding: utf-8 -*-

from odoo import models
from datetime import date, datetime

def date_to_tanggal(st):
    date_split = st.split("-")
    bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober',
             'November', 'Desember']
    return date_split[2] + " " + bulan[int(date_split[1]) - 1] + " " + date_split[0]
class RincianKasBankXlsx(models.AbstractModel):
    _name = 'report.om_account_report.report_rincian_kas_bank_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, stock):
        today = date.today()
        dt = 'Tanggal Print : ' + str(today.strftime("%Y-%m-%d"))
        bold = workbook.add_format({'bold': True, 'border': 1})
        bold_center = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
        title = workbook.add_format({'bold': True, 'align': 'center', 'border': 1, 'bg_color': '#cccccc'})
        format_data = workbook.add_format({'border': 1})

        sheet = workbook.add_worksheet(data['nama_jurnal'])
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 60)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 45)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 60)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 30)
        sheet.set_column('K:K', 30)
        sheet.set_column('L:L', 30)

        sheet.merge_range(0, 0, 0, 8, 'PT. TRIYUDA TOPHERINDO NUSANTARA', bold_center)
        sheet.merge_range(1, 0, 1, 8, 'Rincian ' + data['nama_jurnal'], bold_center)
        sheet.merge_range(2, 0, 2, 8, 'Dari ' + date_to_tanggal(str(data['start'])) + ' - ' + date_to_tanggal(str(data['end'])), bold_center)

        sheet.write(5, 0, 'TANGGAL', title)
        sheet.write(5, 1, 'NO TRANSAKSI', title)
        sheet.write(5, 2, 'KODE AKUN LAWAN', title)
        sheet.write(5, 3, 'NAMA AKUN LAWAN', title)
        sheet.write(5, 4, 'PARTNER', title)
        sheet.write(5, 5, 'KETERANGAN', title)
        sheet.write(5, 6, 'DEBIT', title)
        sheet.write(5, 7, 'KREDIT', title)
        sheet.write(5, 8, 'SALDO', title)

        no_sheet = 6
        sheet.write(no_sheet, 0, '', format_data)
        sheet.write(no_sheet, 1, '', format_data)
        sheet.write(no_sheet, 2, '', format_data)
        sheet.write(no_sheet, 3, '', format_data)
        sheet.write(no_sheet, 4, '', format_data)
        sheet.write(no_sheet, 5, '', format_data)
        sheet.write(no_sheet, 6, '', format_data)
        sheet.write(no_sheet, 7, '', format_data)
        sheet.write(no_sheet, 8, 'Rp ' + str(data['saldo_awal']), format_data)

        no_sheet += 1
        for i in data['data_account']:
            sheet.write(no_sheet, 0, date_to_tanggal(str(i[0])), format_data)
            sheet.write(no_sheet, 1, i[1], format_data)
            sheet.write(no_sheet, 2, i[2], format_data)
            sheet.write(no_sheet, 3, i[3], format_data)
            sheet.write(no_sheet, 4, i[4], format_data)
            sheet.write(no_sheet, 5, i[5], format_data)
            sheet.write(no_sheet, 6, i[6], format_data)
            sheet.write(no_sheet, 7, i[7], format_data)
            sheet.write(no_sheet, 8, i[8], format_data)

            no_sheet += 1