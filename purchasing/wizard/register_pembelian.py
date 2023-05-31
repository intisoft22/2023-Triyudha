# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

from datetime import date
import time

def lengthmonth(year, month):
    if month == 2 and ((year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))):
        return 29
    return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]


def month2name(month):
    return \
        ['Desember', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober',
         'November', 'Desember'][month]

class RegisterPembelianWizard(models.TransientModel):
    _name = "register.pembelian.wizard"
    _description = "Register Pembelian Wizard"
    _order = 'year desc, month desc'

    def month2name(self, month):
        return [0, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                'November', 'December'][month]

    month = fields.Selection(
        [('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'),
         ('7', 'July'),
         ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month',
        required=True, default=lambda *a: str(time.gmtime()[1]))

    year = fields.Integer('Year', required=True, default=lambda *a: time.gmtime()[0])

    supplier = fields.Many2one('res.partner', string="Supplier", required=False, invisible=True)
    all_supplier = fields.Boolean(string="All Supplier", default=True,)

    @api.onchange('all_supplier')
    def _onchange_all_supplier(self):
        for rec in self:
            rec.supplier = False

    def action_print(self):
        jumlah_hari = lengthmonth(self.year, int(self.month))

        vals = []
        total_quantity = 0
        total_dpp = 0
        total_ppn = 0
        total_pph23 = 0
        total_pph22 = 0
        total_jumlah = 0

        for ac in range(1, jumlah_hari + 1):
            ac_date = date(self.year, int(self.month), ac)

            if self.all_supplier == True:
                filter_account = self.env['account.move'].search(
                    [('invoice_date', '=', ac_date), ('move_type', '=', 'in_invoice')])
            else:
                filter_account = self.env['account.move'].search(
                    [('invoice_date', '=', ac_date), ('move_type', '=', 'in_invoice'), ('partner_id', '=', self.supplier.id)])


            today_val = []
            for fa in filter_account:
                for fa_ln in fa.invoice_line_ids:
                    total_quantity += fa_ln.quantity

                    tax_name = []
                    tax_amount = []
                    for it in fa_ln.tax_ids:
                        tax_name.append(it.name)
                        tax_val = {
                            it.name : it.amount
                        }
                        tax_amount.append(tax_val)

                    price_subtotal = fa_ln.price_unit * fa_ln.quantity
                    if 'PPN (INCL)' in tax_name:
                        dpp = (100/111) * price_subtotal
                        ppn = (11/111) * price_subtotal
                    elif 'PPN (EXCL)' in tax_name:
                        dpp = price_subtotal
                        ppn = (11 / 100) * price_subtotal
                    else:
                        dpp = price_subtotal
                        ppn = 0

                    if 'PPH 23' in tax_name:
                        pph23_amount = [d['PPH 23'] for d in tax_amount if 'PPH 23' in d]
                        pph23 = pph23_amount[0] / 100 * dpp
                    else:
                        pph23 = 0

                    if 'PPH 22' in tax_name:
                        pph22_amount = [d['PPH 22'] for d in tax_amount if 'PPH 22' in d]
                        pph22 = pph22_amount[0] / 100 * dpp
                    else:
                        pph22 = 0

                    jumlah = dpp + ppn + pph23 + pph22

                    total_dpp += dpp
                    total_ppn += ppn
                    total_pph23 += pph23
                    total_pph22 += pph22
                    total_jumlah += jumlah

                    new_val = {'date': ac_date,
                            'vendor': fa.partner_id.name,
                            'bill_date': fa.invoice_date,
                            'tax_number': fa.l10n_id_tax_number,
                            'nama_barang': fa_ln.name,
                            'quantity': fa_ln.quantity,
                            'price_unit': fa_ln.price_unit,
                            'coa': fa_ln.account_id.code,
                            'dpp': dpp,
                            'ppn': ppn,
                            'pph23': abs(pph23),
                            'pph22': pph22,
                            'jumlah': abs(jumlah),
                            }
                    today_val.append(new_val)

            if filter_account:
                vals.append(today_val)

        data = {
            'vals': vals,
            'total_dpp': total_dpp,
            'total_ppn': total_ppn,
            'total_pph23': abs(total_pph23),
            'total_pph22': total_pph22,
            'total_jumlah': abs(total_jumlah),
            'total_quantity': total_quantity,
            'month': month2name(int(self.month)),
            'year': str(self.year),
        }

        return self.env.ref('purchasing.report_register_pembelian_xls').report_action(self, data=data)

