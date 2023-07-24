# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import timedelta, date
import dateutil.parser

class RincianKasBankWizard(models.TransientModel):
    _name = "rincian.kas.bank.wizard"
    _description = "Rincian Kas Bank Wizard"

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    journal = fields.Many2one('account.journal', string='Journal',
                                     required=True)
    def action_print_kartu(self):
        saldo_awal = 0
        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days) + 1):
                yield start_date + timedelta(n)
        date_range = []
        for single_date in daterange(self.date_from, self.date_to):
            date_range.append(single_date)


        account_move_line = self.env['account.move.line'].search([
        ])

        list_saldo = []
        for i in account_move_line:

            if i['move_id']['state'] == 'posted' and dateutil.parser.parse(str(i['date'])).date() < self.date_from and i['move_id']['journal_id'] == self.journal and i['account_id'] == self.journal['default_account_id']:
                saldo_awal += i['debit']
                saldo_awal -= i['credit']


        list_account_line = []
        for i in account_move_line:
            if i['move_id']['state'] == 'posted' and dateutil.parser.parse(str(i['date'])).date() in date_range and i['move_id']['journal_id'] == self.journal and i['account_id'] != self.journal['default_account_id']:
                saldo_awal += i['credit']
                saldo_awal -= i['debit']
                list_account_line.append([i['date'], i['name'], i['account_id']['code'], i['account_id']['name'], i['partner_id']['name'], i['name'], i['credit'], i['debit'], saldo_awal])

        data = {
            'nama_jurnal': str(self.journal['name']),
            'start': self.date_from,
            'end': self.date_to,
            'data_account': list_account_line,
            'saldo_awal': saldo_awal
        }

        return self.env.ref('om_account_report.report_rincian_kas_bank_xlsx').report_action(self, data=data)
