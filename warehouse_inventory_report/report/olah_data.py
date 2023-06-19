# -*- coding: utf-8 -*-

from odoo import api, models

class SerahTerima(models.AbstractModel):
    _name = 'report.warehouse_inventory_report.serah_terima_pdf'
    _description = 'Detail Serah Terima'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        arr = []
        jumlah_record = 0
        halaman = 0

        for rec in docs:
            jumlah_record = len(rec.move_ids_without_package)
            jumlah_record2 = len(rec.move_ids_without_package)
            if rec.move_ids_without_package:
                new_list = [rec.move_ids_without_package[i:i + 10] for i in range(0, len(rec.move_ids_without_package), 10)]
            else:
                new_list = False


        if jumlah_record2 <= 10:
            halaman = 1
        else:
            halaman = int(str(jumlah_record2)[::-1]) % 10
            halaman+=1



        jumlah_record = 10 - (jumlah_record % 10)

        for i in range(1, jumlah_record+1):
            arr.append(i)



        return {
            'doc_ids': docids,
            'doc_model': 'stock.picking',
            'docs': docs,
            'data_serah_terima': new_list,
            'sisa_kolom': arr,
            'jumlah_halaman': halaman,
        }