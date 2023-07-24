# -*- coding: utf-8 -*-

from odoo import api, models
from num2words import num2words


def formatrupiah(uang):
    y = str(uang)
    if len(y) <= 3 :
        return 'Rp ' + y
    else :
        p = y[-3:]
        q = y[:-3]
        return   formatrupiah(q) + '.' + p

class BuktiKasMasuk(models.AbstractModel):
    _name = 'report.om_account_report.bukti_kas_masuk_pdf'
    _description = 'Detail Bukti Kas Masuk'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.bank.statement'].browse(docids)
        arr = []

        tmp_list = []
        list_item = []
        co = 0
        co2 = 0
        jumlah_amount = 0
        halaman = 0
        jum_data = 0
        for rec in docs:
            for it in rec.line_ids:
                if it.amount > 0:
                    jum_data += 1
                    co += 1
                    co2 = 0
                    jumlah_amount += int(it.amount)
                    tmp_list.append([it.payment_ref, formatrupiah(int(it.amount))])
                if co == 10:
                    co2 = 1
                    co = 0
                    halaman += 1
                    list_item.append(tmp_list)
                    tmp_list = []
            if co2 == 0:
                halaman += 1
                list_item.append(tmp_list)

        ter = num2words(jumlah_amount, lang="id")
        if co2 == 0:
            for i in range(1, 10-co+1):
                arr.append(i)

        return {
            'doc_ids': docids,
            'doc_model': 'account.bank.statement',
            'docs': docs,
            'data_bukti_bank_masuk': list_item,
            'sisa_kolom': arr,
            'jumlah_halaman': halaman,
            'terbilang': ter,
            'amount': formatrupiah(int(jumlah_amount)),
            'jum': jum_data
        }