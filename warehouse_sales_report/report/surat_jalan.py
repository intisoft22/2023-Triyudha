# -*- coding: utf-8 -*-

from odoo import api, models
from datetime import date, datetime



class SuratJalan(models.AbstractModel):
    _name = 'report.warehouse_sales_report.surat_jalan_pdf'
    _description = 'Detail Surat Jalan'

    @api.model
    def _get_report_values(self, docids, data=None):
        def date_to_tanggal(st):
            date_split = st.split("-")
            bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober',
                     'November', 'Desember']
            return date_split[0] + " " + bulan[int(date_split[1]) - 1] + " " + date_split[2]
        docs = self.env['sale.order'].browse(docids)
        arr = []
        jumlah_record = 0
        co = 0
        today = date.today()
        date_now = str(today.strftime("%d-%m-%Y"))
        halaman = 0

        for rec in docs:
            jumlah_record = len(rec.order_line)
            jumlah_record2 = len(rec.order_line)
            if rec.order_line:
                new_list = [rec.order_line[i:i + 10] for i in
                            range(0, len(rec.order_line), 10)]
            else:
                new_list = False

        if jumlah_record2 <= 10:
            halaman = 1
        else:
            halaman = int(str(jumlah_record2)[::-1]) % 10
            halaman += 1

        jumlah_record = 10 - (jumlah_record % 10)

        for i in range(1, jumlah_record + 1):
            arr.append(i)

        for i in self:
            print(i.price_subtotal, "aaaaaaaaaaaaaaabbbbbbbbbbbcddddd")
            co = co + int(i.price_subtotal)
        return {
            'doc_ids': docids,
            'doc_model': 'sale_order',
            'docs': docs,
            'data_order_pembelian': new_list,
            'sisa_kolom': arr,
            'jumlah_halaman': halaman,
            'date_now': date_to_tanggal(date_now),
            'total': co,
        }
