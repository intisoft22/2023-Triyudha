# -*- coding: utf-8 -*-

from odoo import models
from datetime import datetime

class KartuHutangXlsx(models.AbstractModel):
    _name = 'report.purchasing.report_kartu_hutang_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, purchase):
        bold = workbook.add_format({'bold': True})
        bold_border = workbook.add_format({'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1,})
        bold_center = workbook.add_format({'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center', 'bg_color': 'yellow'})
        date_style = workbook.add_format({'text_wrap': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': 'dd-mmm-yyyy'})
        money_format = workbook.add_format({'text_wrap': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': '#,##0.00'})
        money_format_bold = workbook.add_format({'text_wrap': True, 'num_format': '#,##0.00', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1})
        border = workbook.add_format({'left': 1, 'bottom': 1, 'right': 1, 'top': 1})

        for obj in purchase:
            sheet = workbook.add_worksheet('Kartu Hutang')
            sheet.set_column('A:A', 15)
            sheet.set_column('B:B', 30)
            sheet.set_column('C:C', 20)
            sheet.set_column('D:D', 20)
            sheet.set_column('E:E', 30)
            sheet.set_column('F:F', 20)
            sheet.set_column('G:G', 20)
            sheet.set_column('H:H', 25)
            sheet.set_column('I:I', 15)
            sheet.set_column('J:J', 15)
            sheet.set_column('K:K', 15)
            sheet.set_column('L:L', 15)
            sheet.set_column('M:M', 15)
            sheet.set_column('N:N', 20)

            row = 0
            col = 0
            col_tgl_nota = col + 0
            col_tgl_tempo = col + 1
            col_tgl_today = col + 2
            col_sisa_hari = col + 3
            col_keterangan = col + 4
            col_faktur = col + 5
            col_no_sj = col + 6
            col_tgl_bayar = col + 7
            col_debet = col + 8
            col_ket = col + 9
            col_kredit = col + 10
            col_kredit_bank = col + 10
            col_kredit_kliring = col + 11
            col_kredit_rp = col + 12
            col_sisa = col + 13

            sheet.write(row, col, 'PT. TRIYUDA TOPHERINDO NUSANTARA', bold)
            row += 1
            sheet.write(row, col, 'KARTU HUTANG', bold)
            row += 1
            sheet.write(row, col, data['vendor'], bold)

            row += 2
            sheet.merge_range(row, col_tgl_nota, row + 1, col_tgl_nota, 'Tanggal Nota', bold_center)
            sheet.merge_range(row, col_tgl_tempo, row + 1, col_tgl_tempo, 'Tanggal Jatuh Tempo', bold_center)
            sheet.merge_range(row, col_tgl_today, row + 1, col_tgl_today, 'Tanggal Hari Ini', bold_center)
            sheet.merge_range(row, col_sisa_hari, row + 1, col_sisa_hari, 'Sisa Hari', bold_center)
            sheet.merge_range(row, col_keterangan, row + 1, col_keterangan, 'Keterangan', bold_center)
            sheet.merge_range(row, col_faktur, row + 1, col_faktur, 'No. Faktur', bold_center)
            sheet.merge_range(row, col_no_sj, row + 1, col_no_sj, 'No. SJ', bold_center)
            sheet.merge_range(row, col_tgl_bayar, row + 1, col_tgl_bayar, 'Tgl. Pembayaran / Cair BG', bold_center)
            sheet.merge_range(row, col_debet, row + 1, col_debet, 'Debet', bold_center)
            sheet.merge_range(row, col_ket, row + 1, col_ket, 'Ket', bold_center)
            sheet.merge_range(row, col_kredit, row, col_kredit + 2, 'Kredit', bold_center)
            sheet.write(row + 1, col_kredit_bank, 'Bank & No. BG', bold_center)
            sheet.write(row + 1, col_kredit_kliring, 'Tgl. Kliring', bold_center)
            sheet.write(row + 1, col_kredit_rp, 'Rp.', bold_center)
            sheet.merge_range(row, col_sisa, row + 1, col_sisa, 'Sisa', bold_center)

            row += 2
            sheet.write(row, col_keterangan, 'Saldo Awal', bold)
            sheet.write(row, col_sisa, data['saldo_awal'], money_format)

            for x in data['val']:
                if x['tgl_nota'] != '':
                    tgl_nota = datetime.strptime(x['tgl_nota'], '%Y-%m-%d')
                else:
                    tgl_nota = ''

                if x['tgl_tempo'] != '':
                    tgl_tempo = datetime.strptime(x['tgl_tempo'], '%Y-%m-%d')
                else:
                    tgl_tempo = ''

                if x['tgl_today'] != '':
                    tgl_today = datetime.strptime(x['tgl_today'], '%Y-%m-%d')
                else:
                    tgl_today = ''

                if x['tgl_pembayaran'] != '':
                    tgl_pembayaran = datetime.strptime(x['tgl_pembayaran'], '%Y-%m-%d')
                else:
                    tgl_pembayaran = ''

                row += 1
                sheet.write(row, col_tgl_nota, tgl_nota, date_style)
                sheet.write(row, col_tgl_tempo, tgl_tempo, date_style)
                sheet.write(row, col_tgl_today, tgl_today, date_style)
                sheet.write(row, col_sisa_hari, x['sisa_hari'], border)
                sheet.write(row, col_keterangan, x['keterangan'], border)
                sheet.write(row, col_faktur, x['no_faktur'], border)
                sheet.write(row, col_debet, x['debit'], money_format)
                sheet.write(row, col_tgl_bayar, tgl_pembayaran, date_style)
                sheet.write(row, col_kredit_rp, x['kredit'], money_format)
                sheet.write(row, col_sisa, x['sisa'], money_format)

                sheet.write(row, col_no_sj, x['no_sj'], border)
                sheet.write(row, col_ket, x['ket'], border)
                sheet.write(row, col_kredit_bank, x['kredit_bank'], border)
                sheet.write(row, col_kredit_kliring, x['tgl_kliring'], border)

            if data['val']:
                row += 1
                sheet.write(row, col_debet, data['total_debit'], money_format_bold)
                sheet.write(row, col_kredit_rp, data['total_kredit'], money_format_bold)

                sheet.write(row, col_tgl_nota, '', border)
                sheet.write(row, col_tgl_tempo, '', border)
                sheet.write(row, col_tgl_today, '', border)
                sheet.write(row, col_sisa_hari, '', border)
                sheet.write(row, col_keterangan, '', border)
                sheet.write(row, col_faktur, '', border)
                sheet.write(row, col_tgl_bayar, '', border)
                sheet.write(row, col_sisa, '', border)
                sheet.write(row, col_no_sj, '', border)
                sheet.write(row, col_ket, '', border)
                sheet.write(row, col_kredit_bank, '', border)
                sheet.write(row, col_kredit_kliring, '', border)

                row += 1
                sheet.write(row, col_sisa, data['saldo_akhir'], money_format_bold)
                sheet.write(row, col_tgl_bayar, 'Saldo Akhir', bold_border)

                sheet.write(row, col_tgl_nota, '', border)
                sheet.write(row, col_tgl_tempo, '', border)
                sheet.write(row, col_tgl_today, '', border)
                sheet.write(row, col_sisa_hari, '', border)
                sheet.write(row, col_keterangan, '', border)
                sheet.write(row, col_faktur, '', border)
                sheet.write(row, col_no_sj, '', border)
                sheet.write(row, col_ket, '', border)
                sheet.write(row, col_kredit_bank, '', border)
                sheet.write(row, col_kredit_kliring, '', border)
                sheet.write(row, col_debet, '', border)
                sheet.write(row, col_kredit_rp, '', border)