from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from datetime import timedelta
from odoo.exceptions import UserError


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    def action_done(self):
        for x in self:
            tanggalproses = False
            if x.date_done:
                tanggalproses = x.date_done
                date_done = datetime.strptime(str(tanggalproses), '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
            else:
                tanggalproses=datetime.now()
                date_done = tanggalproses
            bulan = date_done.month
            tahun = date_done.year
            tidakbisacancel = False
            compute_src = compute_dest = False
            card_obj = self.env['stock.card']
            if x.location_id.usage == 'internal':
                compute_src = card_obj.search(
                    [('month', '=', bulan), ('year', '=', tahun), ('location_id', '=', x.location_id.id)])
                if compute_src:
                    if compute_src[0].state not in ['draft','inprogress','cancel']:
                        tidakbisacancel = True
            if x.location_dest_id.usage == 'internal':
                compute_dest = card_obj.search(
                    [('month', '=', bulan), ('year', '=', tahun), ('location_id', '=', x.location_dest_id.id)])
                if compute_dest:
                    if compute_dest[0].state not in ['draft','inprogress','cancel']:
                        tidakbisacancel = True
            # print(saldoawalcompute)

            if tidakbisacancel:

                raise UserError(
                    _("You cannot validate this picking because inventory card already closed, inventory card must be cancel first"))
            else:
                res = super(stock_picking, self).action_done()
                if compute_src:
                    compute_src[0].need_compute = True
                if compute_dest:
                    compute_dest[0].need_compute = True

                return res

    def action_cancel(self):
        for x in self:
            if x.date_done:
                date_done = datetime.strptime(str(x.date_done), '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                bulan = date_done.month
                tahun = date_done.year
                tidakbisacancel = False
                compute_src = compute_dest = False
                card_obj = self.env['stock.card']
                if x.location_id.usage == 'internal':
                    compute_src = card_obj.search(
                        [('month', '=', bulan), ('year', '=', tahun), ('location_id', '=', x.location_id.id)])
                    if compute_src:
                        if compute_src[0].state not in ['draft','inprogress','cancel']:
                            tidakbisacancel = True
                if x.location_dest_id.usage == 'internal':
                    compute_dest = card_obj.search(
                        [('month', '=', bulan), ('year', '=', tahun), ('location_id', '=', x.location_dest_id.id)])
                    if compute_dest:
                        if compute_dest[0].state not in ['draft','inprogress','cancel']:
                            tidakbisacancel = True
                # print(saldoawalcompute)

                if tidakbisacancel:

                    raise UserError(
                        _("You cannot cancel this picking because inventory card already closed, inventory card must be cancel first"))
                else:
                    res = super(stock_picking, self).action_cancel()
                    if compute_src:
                        compute_src[0].need_compute = True
                    if compute_dest:
                        compute_dest[0].need_compute = True

                    return res
            else:
                res = super(stock_picking, self).action_cancel()
                return res
