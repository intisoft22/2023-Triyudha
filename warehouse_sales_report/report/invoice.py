# -*- coding: utf-8 -*-

from odoo import api, models
from datetime import date, datetime
from num2words import num2words
import dateutil.parser

class InvoiceResi(models.AbstractModel):
    _name = 'report.warehouse_sales_report.invoice_pdf'
    _description = 'Detail Invoice'



    @api.model
    def _get_report_values(self, docids, data=None):

        def date_to_tanggal(st):
            date_split = st.split("-")
            bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober',
                     'November', 'Desember']
            return date_split[2] + " " + bulan[int(date_split[1]) - 1] + " " + date_split[0]

        docs = self.env['sale.order'].browse(docids)
        arr = []
        jumlah_record = 0
        co = 0
        today = date.today()
        docs2 = self.env['sale.order'].browse(docids)
        date_now = str(today.strftime("%d-%m-%Y"))
        halaman = 0
        nomor = ""
        ter = num2words(docs.amount_total, lang="id")

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

        for i in docs2:
            for j in i.order_line:
                co = co + int(j.price_subtotal)
        tgl_faktur = str(docs2['date_order'])
        tgl_faktur = dateutil.parser.parse(tgl_faktur).date()
        tgl_faktur = date_to_tanggal(str(tgl_faktur))

        return {
            'doc_ids': docids,
            'doc_model': 'sale_order',
            'docs': docs,
            'data_order_pembelian': new_list,
            'sisa_kolom': arr,
            'jumlah_halaman': halaman,
            'date_now': date_now,
            'total': co,
            'nomor': nomor,
            'amount_total': int(docs.amount_total),
            'amount_total_terbilang': ter,
            'tgl_faktur': tgl_faktur,
        }
