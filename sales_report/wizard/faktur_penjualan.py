# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import timedelta, date

class FakturPenjualanWizard(models.TransientModel):
    _name = "faktur.penjualan.wizard"
    _description = "Faktur Penjualan Wizard"

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    tax = fields.Selection([('all', 'All'),
                            ('non', 'Non'),
                            ('tax', 'Tax'),
                            ], string='Tax', required=True, default='all')


    def action_print(self):
        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days) + 1):
                yield start_date + timedelta(n)

        data = {
            'date_from': self.date_from.strftime('%d %b %Y'),
            'date_to': self.date_to.strftime('%d %b %Y'),
        }

        return self.env.ref('sales_report.report_faktur_penjualan_xls').report_action(self, data=data)
