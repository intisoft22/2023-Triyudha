# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import timedelta, date
import dateutil.parser
from datetime import timedelta, date
import dateutil.parser
import datetime
class CashBankWizard(models.TransientModel):
    _name = "cash.bank.wizard"
    _description = "Cash Bank Wizard"

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    journal = fields.Many2one('account.journal', string='Journal',
                              required=True)

    def action_print_kartu(self):
        saldo_awal = 0
        saldo_awal2 = 0

        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days) + 1):
                yield start_date + timedelta(n)

        date_range = []
        for single_date in daterange(self.date_from, self.date_to):
            date_range.append(single_date)

        account_move_line = self.env['account.move.line'].search([
            ("journal_id", "=", self.journal['name'])
        ])

        list_saldo = []
        for i in account_move_line:
            # date in yyyy/mm/dd format
            d1 = datetime.datetime(int(str(i['date']).split('-')[0]), int(str(i['date']).split('-')[1]),
                                   int(str(i['date']).split('-')[2]))
            d2 = datetime.datetime(int(str(self.date_from).split('-')[0]), int(str(self.date_from).split('-')[1]),
                                   int(str(self.date_from).split('-')[2]))

            if d1 < d2 and str(i['journal_id']['name']) == str(self.journal['name']):

                if i['move_id']['state'] == 'posted' and i['move_id']['journal_id'] == self.journal and i[
                    'account_id'] == self.journal['default_account_id']:
                    saldo_awal += i['debit']
                    saldo_awal -= i['credit']

        saldo_awal2 = saldo_awal

        list_account_line = []
        for i in account_move_line:
            if str(i['journal_id']['name']) == str(self.journal['name']):
                if i['move_id']['state'] == 'posted' and dateutil.parser.parse(str(i['date'])).date() in date_range and \
                        i['move_id']['journal_id'] == self.journal and i['account_id'] != self.journal[
                    'default_account_id']:
                    saldo_awal += i['credit']
                    saldo_awal -= i['debit']
                    list_account_line.append(
                        [i['date'], i['move_id']['name'], i['account_id']['code'], i['account_id']['name'],
                         i['partner_id']['name'], i['name'], i['credit'], i['debit'], saldo_awal])

        data = {
            'nama_jurnal': str(self.journal['name']),
            'start': self.date_from,
            'end': self.date_to,
            'data_account': list_account_line,
            'saldo_awal': saldo_awal2
        }

        return self.env.ref('accounting_excel_report.report_cash_bank_xlsx').report_action(self, data=data)


