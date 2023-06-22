# -*- coding: utf-8 -*-

from odoo import models
from datetime import datetime

class KartuPersediaanXlsx(models.AbstractModel):
    _name = 'report.report_kartu_persediaan.report_kartu_persediaan_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, purchase):
        bold = workbook.add_format({'bold': True})
        bold_border = workbook.add_format({'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1,})
        bold_center = workbook.add_format({'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center', 'bg_color': 'yellow'})
        date_style = workbook.add_format({'text_wrap': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': 'dd-mmm-yyyy'})
        money_format = workbook.add_format({'text_wrap': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': '#,##0.00'})
        int_format = workbook.add_format({'text_wrap': True,'align': 'right', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': '#,##0'})
        float_format = workbook.add_format({'text_wrap': True,'align': 'right', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': '#,##0.00'})
        money_format_bold = workbook.add_format({'text_wrap': True, 'num_format': '#,##0.00', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1})
        border = workbook.add_format({'left': 1, 'bottom': 1, 'right': 1, 'top': 1})

        for obj in purchase:
            sheet = workbook.add_worksheet('Kartu Persediaan')
            sheet.set_column('A:A', 20)

            row = 0
            col = 0
            col_nama = col + 0
            col_satuan = col + 1
            col_awal_pcs = col + 2
            col_awal_kg = col + 3

            if data['is_accounting']:
                col_awal_rp = col + 4
                col_masuk_pcs = col + 5
                col_masuk_kg = col + 6
                col_masuk_rp = col + 7
                col_keluar_pcs = col + 8
                col_keluar_kg = col + 9
                col_keluar_rp = col + 10
                col_akhir_pcs = col + 11
                col_akhir_kg = col + 12
                col_akhir_rp = col + 13
            else:
                col_masuk_pcs = col + 4
                col_masuk_kg = col + 5
                col_keluar_pcs = col + 6
                col_keluar_kg = col + 7
                col_akhir_pcs = col + 8
                col_akhir_kg = col + 9


            sheet.write(row, col, 'POSISI ' + data['product_category'], bold)
            row += 1
            sheet.write(row, col, data['month'] + ' ' + data['year'], bold)
            row += 1
            sheet.write(row, col, 'Tanggal Print : ' + data['today'], bold)

            row += 2
            sheet.merge_range(row, col_nama, row + 1, col_nama, 'Nama Produk', bold_center)
            sheet.merge_range(row, col_satuan, row + 1, col_satuan, 'Satuan', bold_center)

            sheet.write(row + 1, col_awal_pcs, 'Pcs', bold_center)
            sheet.write(row + 1, col_awal_kg, 'Kg', bold_center)

            sheet.write(row + 1, col_masuk_pcs, 'Pcs', bold_center)
            sheet.write(row + 1, col_masuk_kg, 'Kg', bold_center)

            sheet.write(row + 1, col_keluar_pcs, 'Pcs', bold_center)
            sheet.write(row + 1, col_keluar_kg, 'Kg', bold_center)

            sheet.write(row + 1, col_akhir_pcs, 'Pcs', bold_center)
            sheet.write(row + 1, col_akhir_kg, 'Kg', bold_center)

            if data['is_accounting']:
                sheet.merge_range(row, col_awal_pcs, row, col_awal_pcs + 2, 'Saldo Awal', bold_center)
                sheet.write(row + 1, col_awal_rp, 'Rp', bold_center)

                sheet.merge_range(row, col_masuk_pcs, row, col_masuk_pcs + 2, 'Saldo Masuk', bold_center)
                sheet.write(row + 1, col_masuk_rp, 'Rp', bold_center)

                sheet.merge_range(row, col_keluar_pcs, row, col_keluar_pcs + 2, 'Saldo Keluar', bold_center)
                sheet.write(row + 1, col_keluar_rp, 'Rp', bold_center)

                sheet.merge_range(row, col_akhir_pcs, row, col_akhir_pcs + 2, 'Saldo Akhir', bold_center)
                sheet.write(row + 1, col_akhir_rp, 'Rp', bold_center)
            else:
                sheet.merge_range(row, col_awal_pcs, row, col_awal_pcs + 1, 'Saldo Awal', bold_center)
                sheet.merge_range(row, col_masuk_pcs, row, col_masuk_pcs + 1, 'Saldo Masuk', bold_center)
                sheet.merge_range(row, col_keluar_pcs, row, col_keluar_pcs + 1, 'Saldo Keluar', bold_center)
                sheet.merge_range(row, col_akhir_pcs, row, col_akhir_pcs + 1, 'Saldo Akhir', bold_center)

            location_id = self.env['stock.location'].search(
                [('categ_id', '=', obj.product_category.id)], limit=1)
            if not location_id:
                return True

            compute = self.env['stock.card'].search(
                [('month', '=', obj.month), ('year', '=', obj.year), ('location_id', '=', location_id.id),
                 ('state', 'in', ['inprogress', 'done'])],
                limit=1)
            if not compute:
                return True
            else:
                if compute.state == 'inprogress':
                    compute.compute_stock()

                row += 2
                no = 1
                for cl in compute.line_ids:
                    weight=cl.product_id.weight
                    sheet.write(row, col_nama, cl.product_id.name, border)
                    sheet.write(row, col_satuan, cl.product_id.uom_id.name, border)
                    sheet.write(row, col_awal_pcs, cl.saldoawal, int_format)
                    sheet.write(row, col_awal_kg, cl.saldoawal*weight, float_format)

                    sheet.write(row, col_masuk_pcs, cl.masuk, int_format)
                    sheet.write(row, col_masuk_kg,  cl.masuk*weight, float_format)

                    sheet.write(row, col_keluar_pcs, cl.keluar, int_format)
                    sheet.write(row, col_keluar_kg, cl.keluar*weight, float_format)

                    sheet.write(row, col_akhir_pcs, cl.saldoakhir, int_format)
                    sheet.write(row, col_akhir_kg, cl.saldoakhir*weight, float_format)

                    if data['is_accounting']:
                        sheet.write(row, col_awal_rp, '', float_format)
                        sheet.write(row, col_masuk_rp, '', float_format)
                        sheet.write(row, col_keluar_rp, '', float_format)
                        sheet.write(row, col_akhir_rp, '', float_format)

                    row+=1

