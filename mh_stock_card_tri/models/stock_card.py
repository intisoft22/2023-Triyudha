from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import time


def lengthmonth(year, month):
    if month == 2 and ((year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))):
        return 29
    return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]


def month2name(month):
    return \
        ['Desember', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober',
         'November', 'Desember'][month]


class StockCard(models.Model):
    _description = 'Stock Card'
    _name = 'stock.card'
    _order = 'year desc, month desc'

    def month2name(self, month):
        return [0, 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Des'][month]

    name = fields.Char(string='Name', readonly=1)
    warehouse_id = fields.Many2one(
        'stock.warehouse', 'Warehouse', readonly=True,
        ondelete="cascade", required=True,
        states={'draft': [('readonly', False)]})
    location_id = fields.Many2one(
        'stock.location', 'Location', readonly=True,
        domain=[('usage', 'in', ['internal', 'transit'])],
        ondelete="cascade", required=True,
        states={'draft': [('readonly', False)]},
    )
    need_compute = fields.Boolean('Need Compute', readonly=1)
    month = fields.Selection(
        [('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'),
         ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], string='Month',
        required=True,  default=lambda *a: str(time.gmtime()[1]), readonly=True, states={'draft': [('readonly', False)]})
    year = fields.Integer('Year', required=True, default=lambda *a: time.gmtime()[0], readonly=True,
                          states={'draft': [('readonly', False)]})
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('inprogress', 'In Progress'),
            ('done', 'Closed'),
            ('cancel', 'Cancelled'),
        ],
        string='Status', copy=False, default='draft', index=True,
        readonly=True, track_visibility='onchange',
    )
    line_ids = fields.One2many('stock.card.line', 'stockcard_id', string='Product', readonly=True,
                               states={'draft': [('readonly', False)]})

    last_compute = fields.Datetime('Last modified date', readonly=1)

    categ_id = fields.Many2one('product.category', string='Product Category')

    def diff_month(self, d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month

    @api.model
    def create(self, vals):
        upd_vals = vals.copy()

        warehouse_id = upd_vals.get('warehouse_id')
        location_id = upd_vals.get('location_id')
        month = upd_vals.get('month')
        year = upd_vals.get('year')
        warehouse_name = self.env['stock.warehouse'].search([('id', '=', warehouse_id)]).name
        location_name = self.env['stock.location'].search([('id', '=', location_id)]).name
        stockcard = self.env['stock.card'].search(
            [('warehouse_id', '=', warehouse_id), ('location_id', '=', location_id), ('month', '=', int(month)),
             ('state', 'not in', ['draft','cancel']),
             ('year', '=', year)])
        if stockcard:
            raise UserError(_("Monthly Inventory Card for %s %s %s %s already exist" % (
                warehouse_name, location_name, self.month2name(int(month)), year)))
        stockcard = self.env['stock.card'].search(
            [('warehouse_id', '=', warehouse_id), ('location_id', '=', location_id), ('state', 'not in', ['draft','cancel'])])
        if stockcard:

            scnow = datetime(year, int(month), 1)
            stockcard = self.env['stock.card'].search(
                [('warehouse_id', '=', warehouse_id), ('location_id', '=', location_id), ('month', '<=', month),
                 ('state', 'not in', ['draft','cancel']),
                 ('year', '=', year)], order='year desc, month desc')
            if not stockcard:
                stockcard = self.env['stock.card'].search(
                    [('warehouse_id', '=', warehouse_id), ('location_id', '=', location_id), ('state', 'not in', ['draft','cancel']),
                     ('year', '<', year)], order='year desc, month desc')
            for sc in stockcard:
                sclast = datetime(sc.year, int(sc.month), 1)
                delta = self.diff_month(scnow, sclast) - 1
                # print(sclast)
                # print(delta)
                if delta != 0:
                    bulanstring = []
                    for x in range(delta):
                        # print(sc.month + x + 1)
                        # print("===============")
                        bulanstring.append(month2name(int(month) + x + 1))
                    raise UserError(_("you must create Monthly Inventory Stock for %s %s - %s first" % (
                        warehouse_name, location_name, ', '.join(bulanstring))))
                else:

                    name = warehouse_name + "/" + location_name + "-" + self.month2name(int(month)) + " " + str(year)
                    upd_vals['name'] = name
                    return super().create(upd_vals)
        else:

            name = warehouse_name + "/" + location_name + "-" + self.month2name(int(month)) + " " + str(year)
            upd_vals['name'] = name
            return super().create(upd_vals)

    def write(self, values):
        upd_vals = values.copy()
        if upd_vals.get('warehouse_id') or upd_vals.get('location_id') or upd_vals.get('month') or upd_vals.get('year'):

            if upd_vals.get('warehouse_id'):
                warehouse_id = upd_vals.get('warehouse_id')
            else:
                warehouse_id = self.warehouse_id.id
            warehouse_name = self.env['stock.warehouse'].search([('id', '=', warehouse_id)]).name
            if upd_vals.get('location_id'):
                location_id = upd_vals.get('location_id')
            else:
                location_id = self.location_id.id

            location_name = self.env['stock.location'].search([('id', '=', location_id)]).name

            if upd_vals.get('month'):
                month = int(upd_vals.get('month'))
            else:
                month = int(self.month)
            if upd_vals.get('year'):
                year = upd_vals.get('year')
            else:
                year = self.year

            stockcard = self.env['stock.card'].search(
                [('warehouse_id', '=', warehouse_id), ('location_id', '=', location_id), ('month', '=', month),
                 ('state', 'not in', ['draft','cancel']),
                 ('year', '=', year)])
            if stockcard:
                raise UserError(_("Monthly Inventory Card for %s %s %s %s already exist" % (
                    warehouse_name, location_name, self.month2name(int(month)), year)))

            stockcard = self.env['stock.card'].search(
                [('warehouse_id', '=', warehouse_id), ('location_id', '=', location_id), ('state',  'not in', ['draft','cancel'])])
            if stockcard:

                scnow = datetime(year, month, 1)
                stockcard = self.env['stock.card'].search(
                    [('warehouse_id', '=', warehouse_id), ('location_id', '=', location_id), ('month', '<=', month),
                     ('state', 'not in', ['draft','cancel']),
                     ('year', '=', year)])
                if not stockcard:
                    stockcard = self.env['stock.card'].search(
                        [('warehouse_id', '=', warehouse_id), ('location_id', '=', location_id), ('state',  'not in', ['draft','cancel']),
                         ('year', '<', year)])
                for sc in stockcard:
                    sclast = datetime(sc.year, int(sc.month), 1)
                    delta = self.diff_month(scnow, sclast) - 1
                    # print(delta)
                    if delta != 0:
                        bulanstring = []
                        for x in range(delta):
                            bulanstring.append(month2name(int(month) + x + 1))
                        raise UserError(_("you must create Monthly Inventory Stock for %s %s - %s first" % (
                            warehouse_name, location_name, ', '.join(bulanstring))))
                    else:

                        name = warehouse_name + "/" + location_name + "-" + self.month2name(int(month)) + " " + str(year)
                        upd_vals['name'] = name

            else:

                name = warehouse_name + "/" + location_name + "-" + self.month2name(int(month)) + " " + str(year)
                upd_vals['name'] = name

        res = super().write(upd_vals)
        return res

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            self.location_id = False
            warehouseuser = []
            locuser = self.env['stock.location'].search([('name', '=', self.warehouse_id.code)])
            warehouseuser.append(locuser.id)
            location_ids = warehouseuser

            # print(categ_products)
            # print("===============================")
            return {'domain': {'location_id': [('id', 'child_of', location_ids), ('usage', '=', 'internal')]}}
        else:
            self.location_id = False

    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.location_id:
            self.categ_id = self.location_id.categ_id.id

    def action_confirm(self):
        monthseblumnya = int(self.month) - 1
        tahunseblumnya = self.year
        if self.month == 1:
            monthseblumnya = 12
            tahunseblumnya = self.year - 1
        stockcard = self.env['stock.card'].search(
            [('warehouse_id', '=', self.warehouse_id.id), ('location_id', '=', self.location_id.id),
             ('month', '=', monthseblumnya),
             ('state', '!=', 'done'),
             ('year', '=', tahunseblumnya)], order='year desc, month desc')
        if stockcard:
            raise UserError(_("There is no closed Inventory card in the previous period. You must close it first"))
        if self.line_ids:
            self.compute_stock()
            self.state = 'done'
            for line in self.line_ids:
                line.state = 'done'
        else:
            raise UserError(_("Can't confirm Monthly Inventory Card because no calculated Product"))

    def action_start(self):
        self.state = 'inprogress'
        for line in self.line_ids:
            line.state = 'inprogress'

    def action_cancel(self):
        monthsesudah = self.month + 1
        tahunsesudah = self.year
        if self.month == 12:
            monthsesudah = 1
            tahunsesudah = self.year + 1
        stockcard = self.env['stock.card'].search(
            [('warehouse_id', '=', self.warehouse_id.id), ('location_id', '=', self.location_id.id),
             ('month', '=', monthsesudah),
             ('state', '=', 'done'),
             ('year', '=', tahunsesudah)], order='year desc, month desc')
        if stockcard:
            raise UserError(_("There is a newer Inventory card period. You must cancel it first"))
        self.state = 'cancel'
        for line in self.line_ids:
            line.state = 'cancel'

    def action_draft(self):
        self.state = 'draft'
        self.line_ids = False

    def compute_stock(self):
        res = {}

        for sc in self:
            adacateg=False
            if sc.categ_id:
                adacateg=True
                if not sc.line_ids:
                    Product = self.env['product.product']
                    categ_products = Product.search([('categ_id', 'child_of', sc.categ_id.id)])
                    # print(categ_products)
                    for prod in categ_products:
                        val = {'product_id': prod.id,
                               'saldoawal': 0,
                               'masuk': 0,
                               'keluar': 0,
                               'saldoakhir': 0,
                               'stockcard_id': sc.id}
                        line = self.env['stock.card.line'].create(val)
                        line.action_compute()
                else:
                    for l in sc.line_ids:
                        l.saldoawal = 0
                        l.masuk = 0
                        l.keluar = 0
                        l.saldoakhir = 0
            else:

                if sc.line_ids:
                    for line in sc.line_ids:
                        line.unlink()
            if int(sc.month) == 1:
                bulan = 12
                tahun = sc.year - 1
            else:
                bulan = int(sc.month) - 1
                tahun = sc.year

            now = datetime(sc.year, int(sc.month), 1)
            jumlah_hari = lengthmonth(sc.year,int(sc.month))
            end = now + relativedelta(days=jumlah_hari - 1)

            date_awal = (
                    datetime.strptime(now.strftime('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S') - timedelta(
                hours=7)).strftime(
                '%Y-%m-%d %H:%M:%S')
            date_akhir = (
                    datetime.strptime(end.strftime('%Y-%m-%d 23:59:59'), '%Y-%m-%d %H:%M:%S') - timedelta(
                hours=7)).strftime(
                '%Y-%m-%d %H:%M:%S')
            res_stock = {}
            saldoawalcompute = self.search(
                [('month', '=', bulan), ('year', '=', tahun), ('location_id', '=', sc.location_id.id),
                 ('state', '=', 'done')],
                limit=1)
            # print(saldoawalcompute)
            if saldoawalcompute:
                for sa in saldoawalcompute:
                    for sa_line in sa.line_ids:
                        if sa_line.product_id.id not in res_stock:
                            res_stock[sa_line.product_id.id] = {}
                            res_stock[sa_line.product_id.id]['saldoawal'] = sa_line.saldoakhir
                            res_stock[sa_line.product_id.id]['masuk'] = 0
                            res_stock[sa_line.product_id.id]['keluar'] = 0
                            res_stock[sa_line.product_id.id]['saldoakhir'] = sa_line.saldoakhir
                        else:
                            res_stock[sa_line.product_id.id]['saldoawal'] += sa_line.saldoakhir
                            res_stock[sa_line.product_id.id]['masuk'] = 0
                            res_stock[sa_line.product_id.id]['keluar'] = 0
                            res_stock[sa_line.product_id.id]['saldoakhir'] += sa_line.saldoakhir
            else:

                saldoawalcompute = self.search(
                    [('location_id', '=', sc.location_id.id), ('state', '=', 'done'), ('year', '=', tahun),
                     ('month', '<=', bulan)], limit=1, order="year desc, month desc")
                if not saldoawalcompute:
                    saldoawalcompute = self.search(
                        [('location_id', '=', sc.location_id.id), ('state', '=', 'done'), ('year', '<=', tahun)],
                        limit=1, order="year desc, month desc")

                if saldoawalcompute:
                    for sa in saldoawalcompute:
                        for sa_line in sa.line_ids:
                            if sa_line.product_id.id not in res_stock:
                                res_stock[sa_line.product_id.id] = {}
                                res_stock[sa_line.product_id.id]['saldoawal'] = sa_line.saldoakhir
                                res_stock[sa_line.product_id.id]['masuk'] = 0
                                res_stock[sa_line.product_id.id]['keluar'] = 0
                                res_stock[sa_line.product_id.id]['saldoakhir'] = sa_line.saldoakhir
                            else:
                                res_stock[sa_line.product_id.id]['saldoawal'] += sa_line.saldoakhir
                                res_stock[sa_line.product_id.id]['masuk'] = 0
                                res_stock[sa_line.product_id.id]['keluar'] = 0
                                res_stock[sa_line.product_id.id]['saldoakhir'] += sa_line.saldoakhir

                        bulansaldoawal = sa.month
                        tahunsaldoawal = sa.year
                        jumlah_harisaldoawal = lengthmonth(tahunsaldoawal, bulansaldoawal)
                        startsaldoawal = datetime(tahunsaldoawal, bulansaldoawal, jumlah_harisaldoawal)
                        startsaldoawal = startsaldoawal + relativedelta(days=1)
                        endsaldoawal = datetime(sc.year, int(sc.month), 1)
                        endsaldoawal = endsaldoawal - relativedelta(days=1)
                        # print(startsaldoawal)
                        # print(endsaldoawal)
                        date_awalsaldo = (
                                datetime.strptime(startsaldoawal.strftime('%Y-%m-%d 00:00:00'),
                                                  '%Y-%m-%d %H:%M:%S') - timedelta(
                            hours=7)).strftime(
                            '%Y-%m-%d %H:%M:%S')
                        date_akhirsaldo = (
                                datetime.strptime(endsaldoawal.strftime('%Y-%m-%d 23:59:59'),
                                                  '%Y-%m-%d %H:%M:%S') - timedelta(
                            hours=7)).strftime(
                            '%Y-%m-%d %H:%M:%S')

                        masuk = self.env['stock.move'].search(
                            [('location_dest_id', 'child_of', sc.location_id.id), ('state', '=', 'done'),
                             ('date', '<=', date_akhirsaldo),
                             ('date', '>=', date_awalsaldo)])

                        for m in masuk:
                            if m.product_id.id not in res_stock:
                                res_stock[m.product_id.id] = {}
                                res_stock[m.product_id.id]['saldoawal'] = m.product_uom_qty
                                res_stock[m.product_id.id]['masuk'] = 0
                                res_stock[m.product_id.id]['keluar'] = 0
                                res_stock[m.product_id.id]['saldoakhir'] = m.product_uom_qty
                            else:
                                res_stock[m.product_id.id]['saldoawal'] += m.product_uom_qty
                                res_stock[m.product_id.id]['saldoakhir'] += m.product_uom_qty

                        keluar = self.env['stock.move'].search(
                            [('location_id', 'child_of', sc.location_id.id), ('state', '=', 'done'),
                             ('date', '<=', date_akhirsaldo),
                             ('date', '>=', date_awalsaldo)])

                        for k in keluar:
                            if k.product_id.id not in res_stock:
                                res_stock[k.product_id.id] = {}
                                res_stock[k.product_id.id]['saldoawal'] = 0 - k.product_uom_qty
                                res_stock[k.product_id.id]['masuk'] = 0
                                res_stock[k.product_id.id]['keluar'] = 0
                                res_stock[k.product_id.id]['saldoakhir'] = 0 - k.product_uom_qty
                            else:
                                res_stock[k.product_id.id]['saldoawal'] -= k.product_uom_qty
                                res_stock[k.product_id.id]['saldoakhir'] -= k.product_uom_qty
                else:
                    endsaldoawal = datetime(sc.year, int(sc.month), 1)
                    endsaldoawal = endsaldoawal - relativedelta(days=1)
                    # print(endsaldoawal)
                    date_akhirsaldo = (
                            datetime.strptime(endsaldoawal.strftime('%Y-%m-%d 23:59:59'),
                                              '%Y-%m-%d %H:%M:%S') - timedelta(
                        hours=7)).strftime(
                        '%Y-%m-%d %H:%M:%S')

                    masuk = self.env['stock.move'].search(
                        [('location_dest_id', 'child_of', sc.location_id.id), ('state', '=', 'done'),
                         ('date', '<=', date_akhirsaldo)])

                    for m in masuk:
                        if m.product_id.id not in res_stock:
                            res_stock[m.product_id.id] = {}
                            res_stock[m.product_id.id]['saldoawal'] = m.product_uom_qty
                            res_stock[m.product_id.id]['masuk'] = 0
                            res_stock[m.product_id.id]['keluar'] = 0
                            res_stock[m.product_id.id]['saldoakhir'] = m.product_uom_qty
                        else:
                            res_stock[m.product_id.id]['saldoawal'] += m.product_uom_qty
                            res_stock[m.product_id.id]['saldoakhir'] += m.product_uom_qty

                    keluar = self.env['stock.move'].search(
                        [('location_id', 'child_of', sc.location_id.id), ('state', '=', 'done'),
                         ('date', '<=', date_akhirsaldo)])

                    for k in keluar:
                        if k.product_id.id not in res_stock:
                            res_stock[k.product_id.id] = {}
                            res_stock[k.product_id.id]['saldoawal'] = 0 - k.product_uom_qty
                            res_stock[k.product_id.id]['masuk'] = 0
                            res_stock[k.product_id.id]['keluar'] = 0
                            res_stock[k.product_id.id]['saldoakhir'] = 0 - k.product_uom_qty
                        else:
                            res_stock[k.product_id.id]['saldoawal'] -= k.product_uom_qty
                            res_stock[k.product_id.id]['saldoakhir'] -= k.product_uom_qty

            masuk = self.env['stock.move'].search(
                [('location_dest_id', 'child_of', sc.location_id.id), ('state', '=', 'done'),
                 ('date', '<=', date_akhir),
                 ('date', '>=', date_awal)])

            for m in masuk:
                if m.product_id.id not in res_stock:
                    res_stock[m.product_id.id] = {}
                    res_stock[m.product_id.id]['saldoawal'] = 0
                    res_stock[m.product_id.id]['masuk'] = m.product_uom_qty
                    res_stock[m.product_id.id]['keluar'] = 0
                    res_stock[m.product_id.id]['saldoakhir'] = m.product_uom_qty
                else:
                    res_stock[m.product_id.id]['masuk'] += m.product_uom_qty
                    res_stock[m.product_id.id]['saldoakhir'] += m.product_uom_qty

            keluar = self.env['stock.move'].search(
                [('location_id', 'child_of', sc.location_id.id), ('state', '=', 'done'), ('date', '<=', date_akhir),
                 ('date', '>=', date_awal)])

            for k in keluar:
                if k.product_id.id not in res_stock:
                    res_stock[k.product_id.id] = {}
                    res_stock[k.product_id.id]['keluar'] = k.product_uom_qty
                    res_stock[k.product_id.id]['saldoakhir'] = 0 - k.product_uom_qty
                else:
                    res_stock[k.product_id.id]['keluar'] += k.product_uom_qty
                    res_stock[k.product_id.id]['saldoakhir'] -= k.product_uom_qty
            if not adacateg:
                for k, v in res_stock.items():
                    val = {'product_id': k,
                           'saldoawal': v['saldoawal'],
                           'masuk': v['masuk'],
                           'keluar': v['keluar'],
                           'saldoakhir': v['saldoakhir'],
                           'stockcard_id': sc.id}
                    line = self.env['stock.card.line'].create(val)
                    line.action_compute()
            else:
                for k, v in res_stock.items():
                    val = {
                        'saldoawal': v['saldoawal'],
                        'masuk': v['masuk'],
                        'keluar': v['keluar'],
                        'saldoakhir': v['saldoakhir']}
                    line = self.env['stock.card.line'].search([('product_id', '=', k), ('stockcard_id', '=', sc.id)])
                    if line:
                        line.saldoawal = v['saldoawal']
                        line.masuk = v['masuk']
                        line.keluar = v['keluar']
                        line.saldoakhir = v['saldoakhir']
                        line.line_ids = False
                        line.action_compute()
            self.last_compute=datetime.strftime((datetime.now()),'%Y-%m-%d %H:%M:%S')
            self.need_compute=False
            # print(res_stock)


class StockCardLine(models.Model):
    _description = 'Stock Card line'
    _name = 'stock.card.line'

    stockcard_id = fields.Many2one(
        'stock.card', 'Stock Card', readonly=True,
        ondelete="cascade",

    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('inprogress', 'In Progress'),
            ('done', 'Closed'),
            ('cancel', 'Cancelled'),
        ],
        string='Status', copy=False, default='draft', index=True,
        readonly=True, track_visibility='onchange',
    )
    product_id = fields.Many2one('product.product', 'Product', readonly=True, )
    saldoawal = fields.Float('Beginning Stock', readonly=True, )
    masuk = fields.Float('Stock In', readonly=True)
    keluar = fields.Float('Stock Out', readonly=True, )
    saldoakhir = fields.Float('Ending Stock', readonly=True)
    line_ids = fields.One2many('stock.card.line.detail', 'stockcardline_id', string='Transaction', readonly=True, )

    def action_compute(self):
        saldoawal = self.saldoawal

        # cwsaldoawal = 0
        # if self.product_id.catch_weight_ok:
        #     cwsaldoawal = self.saldoawal * self.product_id.average_cw_quantity

        val = {'stockcardline_id': self.id,
               'product_id': self.product_id.id,
               'move_id': False,
               'picking_id': False,
               'date': False,
               'origin': 'Saldo Awal',
               'type': False,
               'masuk': 0,
               # 'cwmasuk': 0,
               'keluar': 0,
               # 'cwkeluar': 0,
               'saldoakhir': self.saldoawal,
               # 'cwsaldoakhir': cwsaldoawal,
               }
        self.env['stock.card.line.detail'].create(val)
        now = datetime(self.stockcard_id.year, int(self.stockcard_id.month), 1)
        jumlah_hari = lengthmonth(self.stockcard_id.year, int(self.stockcard_id.month))
        end = now + relativedelta(days=jumlah_hari - 1)

        date_awal = (
                datetime.strptime(now.strftime('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S') - timedelta(
            hours=7)).strftime(
            '%Y-%m-%d %H:%M:%S')
        date_akhir = (
                datetime.strptime(end.strftime('%Y-%m-%d 23:59:59'), '%Y-%m-%d %H:%M:%S') - timedelta(
            hours=7)).strftime(
            '%Y-%m-%d %H:%M:%S')

        domain = [('product_id', '=', self.product_id.id),
                  ('state', '=', 'done'),
                  ('date', '<=', date_akhir),
                  ('date', '>=', date_awal)]
        domain += ['|', ('location_dest_id', 'child_of', self.stockcard_id.location_id.id),
                   ('location_id', 'child_of', self.stockcard_id.location_id.id)]
        # print(domain)
        masuk = self.env['stock.move'].search(domain, order="date asc")

        locationstock = self.env['stock.location'].search([('id', 'child_of', self.stockcard_id.location_id.id)])
        # masuk = self.env['stock.move'].search(
        #     [('product_id', '=', self.product_id.id),
        #      ('location_dest_id', 'child_of', self.stockcard_id.location_id.id), ('state', '=', 'done'),
        #      ('date', '<=', date_akhir),
        #      ('date', '>=', date_awal)])

        for m in masuk:
            type = False
            if m.picking_id:
                if m.picking_id.partner_id:
                    type = 'Partner'
                else:
                    type = 'Internal'
            else:
                type = 'Virtual'
            if m.location_dest_id in locationstock:
                saldoawal += m.product_uom_qty
                # cwsaldoawal += m.product_cw_uom_qty
                val = {'product_id': m.product_id.id,
                       'move_id': m.id,
                       'picking_id': m.picking_id.id,
                       'date': m.date,
                       'origin': m.picking_id.origin,
                       'type': type,
                       'masuk': m.product_uom_qty,
                       # 'cwmasuk': m.product_cw_uom_qty,
                       'keluar': 0,
                       # 'cwkeluar': 0,
                       'saldoakhir': saldoawal,
                       # 'cwsaldoakhir': cwsaldoawal,
                       'stockcardline_id': self.id, }

            if m.location_id in locationstock:
                saldoawal -= m.product_uom_qty
                # cwsaldoawal -= m.product_cw_uom_qty
                val = {'product_id': m.product_id.id,
                       'move_id': m.id,
                       'picking_id': m.picking_id.id,
                       'date': m.date,
                       'origin': m.picking_id.origin,
                       'type': type,
                       'masuk': 0,
                       # 'cwmasuk': 0,
                       'keluar': m.product_uom_qty,
                       # 'cwkeluar': m.product_cw_uom_qty,
                       'saldoakhir': saldoawal,
                       # 'cwsaldoakhir': cwsaldoawal,
                       'stockcardline_id': self.id, }

            self.env['stock.card.line.detail'].create(val)

    def action_open(self):
        for sc in self:
            view_id = \
                self.env['ir.model.data'].get_object_reference('mh_stock_card_tri', 'view_stock_card_line_form_detail')[1]
            if sc.state == 'done':

                ret = {
                    'type': 'ir.actions.act_window',
                    'name': 'Inventory Card',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'res_id': sc.id,
                    'res_model': 'stock.card.line',
                    'target': 'new', 'flags': {'mode': 'readonly'}
                }
                return ret
            else:

                ret = {
                    'type': 'ir.actions.act_window',
                    'name': 'Inventory Card',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'res_id': sc.id,
                    'res_model': 'stock.card.line',
                    'target': 'new', 'flags': {'mode': 'readonly'}
                }
                return ret


class StockCardLineDetail(models.Model):
    _description = 'Stock Card line Detail'
    _name = 'stock.card.line.detail'

    stockcardline_id = fields.Many2one(
        'stock.card.line', 'Stock Card Line', readonly=True,
        ondelete="cascade",

    )

    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    move_id = fields.Many2one('stock.move', 'Stock Move', readonly=True)
    picking_id = fields.Many2one('stock.picking', 'Stock Picking', readonly=True)
    date = fields.Datetime('Date')
    origin = fields.Char('Source Document')
    type = fields.Selection(
        [('Partner', 'Partner'), ('Internal', 'Internal'), ('Virtual', 'Virtual'), ], 'Type')
    saldoawal = fields.Float('Beginning Stock', readonly=True, )
    cwsaldoawal = fields.Float('CW Beginning Stock', readonly=True, )
    masuk = fields.Float('Qty In', readonly=True, )
    cwmasuk = fields.Float('CW Qty In', readonly=True, )
    keluar = fields.Float('Qty Out', readonly=True, )
    cwkeluar = fields.Float('CW Qty Out', readonly=True, )
    saldoakhir = fields.Float('Ending Stock', readonly=True, )
    cwsaldoakhir = fields.Float('CW Ending Stock', readonly=True, )
