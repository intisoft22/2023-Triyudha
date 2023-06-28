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

class LaporanPiutangWizard(models.TransientModel):
    _name = "laporan.piutang.wizard"
    _description = "Laporan Piutang Wizard"
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

    def action_print(self):

        data = {
            'month': month2name(int(self.month)),
            'year': str(self.year),
        }

        return self.env.ref('sales_report.report_laporan_piutang_xls').report_action(self, data=data)
