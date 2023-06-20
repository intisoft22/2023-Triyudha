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


class KartuPersediaanWizard(models.TransientModel):
    _name = "kartu.persediaan.wizard"
    _description = "Kartu Persediaan Wizard"
    _order = 'year desc, month desc'

    def month2name(self, month):
        return [0, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                'November', 'December'][month]

    month = fields.Selection(
        [('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'),
         ('7', 'July'),
         ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Bulan',
        required=True, default=lambda *a: str(time.gmtime()[1]))

    year = fields.Integer('Tahun', required=True, default=lambda *a: time.gmtime()[0])

    product_category = fields.Many2one('product.category', string="Kategori Produk",
                                       domain=[('parent_id', '=', False)], required=True)

    is_accounting = fields.Boolean(string='Default Accounting')

    def action_print(self):
        today = date.today()
        formatted_date = today.strftime("%d/%m/%Y")

        data = {
            'month': month2name(int(self.month)),
            'year': str(self.year),
            'is_accounting': self.is_accounting,
            'product_category': self.product_category.name,
            'today': formatted_date
        }

        return self.env.ref('report_kartu_persediaan.report_kartu_persediaan_xls').report_action(self, data=data)
