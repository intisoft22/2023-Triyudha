# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import timedelta, date

class KartuHutangWizard(models.TransientModel):
    _name = "kartu.hutang.wizard"
    _description = "Kartu Hutang Wizard"

    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')
    partner_id = fields.Many2one('res.partner', string="Partner's", required=True)
    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)


    def action_print(self):
        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days) + 1):
                yield start_date + timedelta(n)

        account_line = self.env['account.move.line'].search([])

        if self.target_move == 'posted':
            saldo_awal = account_line.search([
                ('date', '<', self.date_from),
                ('parent_state', '=', self.target_move),
                ('partner_id', '=', self.partner_id.id),
            ])
        else:
            saldo_awal = account_line.search([
                ('date', '<', self.date_from),
                ('partner_id', '=', self.partner_id.id),
            ])

        sum_saldo = 0
        for sa in saldo_awal:
            if 'piutang' in sa.account_id.name.lower():
                saldo = sa.debit - sa.credit
                sum_saldo += saldo


        val = []
        total_debit = 0
        total_kredit = 0
        prev_sisa = 0
        i = 0
        for single_date in daterange(self.date_from, self.date_to):
            if self.target_move == 'posted':
                filter_account_line = account_line.search([
                    ('date', '=', single_date),
                    ('parent_state', '=', self.target_move),
                    ('partner_id', '=', self.partner_id.id),
                ])
            else:
                filter_account_line = account_line.search([
                    ('date', '=', single_date),
                    ('partner_id', '=', self.partner_id.id),
                ])

            for fal in filter_account_line:
                if 'piutang' in fal.account_id.name.lower():
                    i += 1
                    if i == 1:
                        prev_sisa = sum_saldo + (fal.debit - fal.credit)
                    else:
                        prev_sisa = prev_sisa + (fal.debit - fal.credit)

                    if fal.debit <= 0:
                        tgl_nota = ''
                        tgl_tempo = ''
                        tgl_today = ''
                        sisa_hari = ''
                        no_faktur = ''
                        debit = ''
                    else:
                        tgl_nota = fal.date
                        tgl_tempo = fal.date_maturity
                        tgl_today = date.today()
                        sisa_hari = int((tgl_tempo - tgl_today).days)

                        debit = fal.debit
                        total_debit += fal.debit

                        if fal.move_id.l10n_id_tax_number:
                            no_faktur = fal.move_id.l10n_id_tax_number
                        else:
                            no_faktur = ''

                    if fal.credit <= 0:
                        tgl_pembayaran = ''
                        kredit = ''
                    else:
                        tgl_pembayaran = fal.date
                        kredit = fal.credit
                        total_kredit += fal.credit

                    if fal.name:
                        keterangan = fal.name
                    else:
                        keterangan = ''

                    stock_picking = fal.move_id.picking_ids
                    if stock_picking:
                        for s in stock_picking:
                            if s.no_surat_supplier:
                                no_sj = s.name + (" (") + s.no_surat_supplier + ")"
                            else:
                                no_sj = s.name + (" () ")
                    else:
                        no_sj = ' '

                    new_val = {'tgl_nota': tgl_nota,
                               'tgl_tempo': tgl_tempo,
                               'tgl_today': tgl_today,
                               'sisa_hari': sisa_hari,
                               'keterangan': keterangan,
                               'no_faktur': no_faktur,
                               'debit': debit,
                               'tgl_pembayaran': tgl_pembayaran,
                               'kredit': kredit,
                               'sisa': prev_sisa,
                               'no_sj': no_sj,
                               'ket': '',
                               'kredit_bank': '',
                               'tgl_kliring': '',
                               }

                    val.append(new_val)

            saldo_akhir = prev_sisa

        data = {
            'vendor': self.partner_id.name,
            'saldo_awal': sum_saldo,
            'saldo_akhir': saldo_akhir,
            'val': val,
            'total_debit': total_debit,
            'total_kredit': total_kredit,
        }


        return self.env.ref('purchasing.report_kartu_hutang_xls').report_action(self, data=data)
