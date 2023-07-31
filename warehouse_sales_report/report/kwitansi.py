# -*- coding: utf-8 -*-

from odoo import api, models
from datetime import date, datetime
from num2words import num2words



class OrderPembelian(models.AbstractModel):
    _name = 'report.warehouse_sales_report.kwitansi_pdf'
    _description = 'Detail Kwitansi'



    @api.model
    def _get_report_values(self, docids, data=None):

        def date_to_tanggal(st):
            date_split = st.split("-")
            bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober',
                     'November', 'Desember']
            return date_split[0] + " " + bulan[int(date_split[1]) - 1] + " " + date_split[2]

        # dt = "1/01/2023" hari bulan tahun
        def uang_idr(nominal):
            x = str(nominal)
            if len(x) <= 3:
                return x
            else:
                a = x[:-3]
                b = x[-3:]
                return uang_idr(a) + ',' + b
        ter =  0
        ter = num2words(ter, lang="id")
        docs = self.env['account.payment'].browse(docids)
        for i in docs:
            ter = int(i['amount'])
            nominal = ter
        ter = num2words(ter, lang="id")
        return {
            'doc_ids': docids,
            'doc_model': 'account_payment',
            'docs': docs,
            'amount_total_terbilang': ter,
            'amount_total': uang_idr(int(nominal))
        }
