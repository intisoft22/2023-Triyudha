# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import content_disposition, request
import io

from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from pytz import timezone
import xlsxwriter

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

def set_date(obj_date):
    if obj_date:
        date_utc = datetime.strptime(str(obj_date), '%Y-%m-%d %H:%M:%S')
        date_utc = timezone('Asia/Jakarta').localize(date_utc)
        tz = timezone('UTC')
        date_tz = date_utc
        date = date_tz.strftime('%d %b %Y')
        return date


def set_date2(obj_date):
    date_utc = datetime.strptime(str(obj_date), '%Y-%m-%d')
    date_tz = date_utc
    date = date_tz.strftime('%d %b %Y')
    return date


def set_date3(obj_date):
    bln_array = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober',
                 'November', 'Desember']
    date_utc = datetime.strptime(str(obj_date), '%Y-%m-%d')
    date_utc = timezone('UTC').localize(date_utc)
    date_tz = date_utc.astimezone(timezone('Asia/Jakarta'))
    bln = int(date_tz.strftime('%m'))
    date = date_tz.strftime('%d/%m/%Y')
    return date


def month2name(month):
    return [0, 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Des'][month]


def lengthmonth(year, month):
    if month == 2 and ((year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))):
        return 29
    return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]


class InventoryCardExcelReportController(http.Controller):
    @http.route([
        '/inventory_card/excel_report/<model("inventory.card.report.wizard"):wizard>',
    ], type='http', auth="user", csrf=False)
    def get_inventory_card_excel_report(self, wizard=None, **args):
        # wizard ini adalah model yang dikirim dengan method get_excel_report
        # pada model ng.sale.wizard
        # berisi data sales person, tanggal mulai dan tanggal akhir

        # buat response dengan header berupa file excel
        # agar browser segera mendownload response
        # header Content-Disposition ini adalah nama file
        # isi sesuai kebutuhan

        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Inventory Card Report in Excel Format' + '.xlsx'))
            ]
        )

        # buat object workbook dari library xlsxwriter
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # buat style untuk mengatur jenis font, ukuran font, border dan alligment
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 13, 'bold': True, 'align': 'left'})
        header_style = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center'})
        text_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'left'})

        text_style_number = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right'})

        text_style_number.set_num_format('#,##0')
        text_style_persen = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right'})

        text_style_persen.set_num_format('0"%"')
        number_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right'})

        # loop user / sales person yang dipilih
        # buat worksheet / tab per user

        now = datetime.strptime(str(wizard.tglawal) + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        bulan = now.month
        tahun = now.year
        location = wizard.location_id.id
        # print("bulan", bulan)
        end = datetime.strptime(str(wizard.tglakhir) + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        date_awal = (
                datetime.strptime(now.strftime('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S') - timedelta(
            hours=7)).strftime(
            '%Y-%m-%d %H:%M:%S')
        date_akhir = (
                datetime.strptime(end.strftime('%Y-%m-%d 23:59:59'), '%Y-%m-%d %H:%M:%S') - timedelta(
            hours=7)).strftime(
            '%Y-%m-%d %H:%M:%S')
        saldoawalcompute = request.env['stock.card'].search(
            [('location_id', '=', location), ('state', '=', 'done'), ('year', '=', tahun), ('month', '<', bulan)],
            order="year desc, month desc", limit=1)
        if not saldoawalcompute:
            saldoawalcompute = request.env['stock.card'].search(
                [('location_id', '=', location), ('state', '=', 'done'), ('year', '<', tahun)],
                order="year desc, month desc", limit=1)
        # print(saldoawalcompute)
        saldoawal={}
        productarray=[]
        for product in wizard.product_ids:

            productarray.append(product.id)
            saldoawal[product.id] = {}
            saldoawal[product.id]['saldoawal'] =0

        if saldoawalcompute:
            saldoawalcomputeline = request.env['stock.card.line'].search(
                [('stockcard_id', '=', saldoawalcompute.id), ('product_id', 'in', productarray),])

            for s in saldoawalcomputeline:
                saldoawal[s.product_id.id] = {}
                saldoawal[s.product_id.id]['saldoawal'] = s.saldoakhir

            bulansaldoawal = saldoawalcompute.month
            tahunsaldoawal = saldoawalcompute.year
            jumlah_harisaldoawal = lengthmonth(tahunsaldoawal, bulansaldoawal)
            startsaldoawal = datetime(tahunsaldoawal, bulansaldoawal, jumlah_harisaldoawal)
            startsaldoawal = startsaldoawal + relativedelta(days=1)
            # print(startsaldoawal)
            date_awalsaldo = (
                    datetime.strptime(startsaldoawal.strftime('%Y-%m-%d 00:00:00'),
                                      '%Y-%m-%d %H:%M:%S') - timedelta(
                hours=7)).strftime(
                '%Y-%m-%d %H:%M:%S')
            date_akhirsaldo =date_awal

            masuk = request.env['stock.move'].search(
                [('location_dest_id', 'child_of', location), ('product_id', 'in', productarray), ('state', '=', 'done'),
                 ('date', '<=', date_akhirsaldo),
                 ('date', '>=', date_awalsaldo)])

            for m in masuk:
                if m.product_id.id not in saldoawal:
                    saldoawal[m.product_id.id] = {}
                    saldoawal[m.product_id.id]['saldoawal'] = m.product_uom_qty
                else:
                    saldoawal[m.product_id.id]['saldoawal'] += m.product_uom_qty

            keluar = request.env['stock.move'].search(
                [('location_id', 'child_of', location), ('product_id', 'in', productarray), ('state', '=', 'done'),
                 ('date', '<=', date_akhirsaldo),
                 ('date', '>=', date_awalsaldo)])

            for k in keluar:
                if k.product_id.id not in saldoawal:
                    saldoawal[k.product_id.id] = {}
                    saldoawal[k.product_id.id]['saldoawal'] = 0 - k.product_uom_qty
                else:
                    saldoawal[k.product_id.id]['saldoawal'] -= k.product_uom_qty
            # print(saldoawalcompute)
        else:
            date_akhirsaldo = date_awal

            masuk = request.env['stock.move'].search(
                [('location_dest_id', 'child_of',location), ('product_id', 'in', productarray), ('state', '=', 'done'),
                 ('date', '<=', date_akhirsaldo)])

            for m in masuk:
                if m.product_id.id not in saldoawal:
                    saldoawal[m.product_id.id] = {}
                    saldoawal[m.product_id.id]['saldoawal'] = m.product_uom_qty
                else:
                    saldoawal[m.product_id.id]['saldoawal'] += m.product_uom_qty

            keluar = request.env['stock.move'].search(
                [('location_id', 'child_of', location), ('product_id', 'in', productarray), ('state', '=', 'done'),
                 ('date', '<=', date_akhirsaldo)])

            for k in keluar:
                if k.product_id.id not in saldoawal:
                    saldoawal[k.product_id.id] = {}
                    saldoawal[k.product_id.id]['saldoawal'] = 0 - k.product_uom_qty
                else:
                    saldoawal[k.product_id.id]['saldoawal'] -= k.product_uom_qty
        # print(saldoawal)
        for product in wizard.product_ids:


            warna = ''
            for x in product.attribute_value_ids:
                warna = x.name
            sheet = workbook.add_worksheet(product.default_code[0:10] + " " + warna)
            # set orientation jadi landscape
            sheet.set_landscape()
            # set ukuran kertas, 9 artinya kertas A4
            sheet.set_paper(9)
            # set margin kertas dalam satuan inchi
            sheet.set_margins(0.5, 0.5, 0.5, 0.5)

            # set lebar kolom
            sheet.set_column('A:A', 5)
            sheet.set_column('B:N', 15)

            # judul report

            # merge cell A1 sampai E1 dengan ukuran font 14 dan bold
            sheet.merge_range('A1:F1', 'Kartu Stock', title_style)
            sheet.write('A2:A2', 'Product', title_style)
            sheet.merge_range('B2:F2', ': [' + str(product.default_code) + "] " + product.name+ " " + warna, title_style)
            sheet.write('A3:A3', 'Periode', title_style)
            sheet.merge_range('B3:F3', ': ' + str(set_date(now)) + ' - ' + str(set_date(end)), title_style)

            # judul tabel
            sheet.write(5, 0, 'No.', header_style)
            sheet.write(5, 1, 'Date', header_style)
            sheet.write(5, 2, 'Source Document', header_style)
            sheet.write(5, 3, 'Qty In', header_style)
            sheet.write(5, 4, 'Qty Out', header_style)
            sheet.write(5, 5, 'Ending Stock', header_style)

            row = 6
            number = 1
            saldoawal2=saldoawal[product.id]['saldoawal']
            sheet.write(row, 0, number, text_style)
            sheet.write(row, 1, '', text_style)
            sheet.write(row, 2, 'Saldo Awal', text_style)
            sheet.write(row, 3, ' ', text_style_number)
            sheet.write(row, 4, ' ', text_style_number)
            sheet.write(row, 5, saldoawal2, text_style_number)

            row += 1
            number += 1
            domain=[('product_id', '=', product.id),
                  ('state', '=', 'done'),
                 ('date', '<=', date_akhir),
                 ('date', '>=', date_awal)]
            domain += ['|',('location_dest_id', 'child_of', location),('location_id', 'child_of', location)]
            # print(domain)
            masuk = request.env['stock.move'].search(domain,order="date asc")
            # print(masuk)
            locationstock= request.env['stock.location'].search([('id', 'child_of', location)])
            totalmasuk=0
            totalkeluar=0
            for m in masuk:
                if m.location_dest_id in locationstock:
                    saldoawal2 += m.product_uom_qty
                    totalmasuk += m.product_uom_qty
                    sheet.write(row, 0, number, text_style)
                    sheet.write(row, 1, set_date(m.date), text_style)
                    sheet.write(row, 2, m.picking_id.origin or m.name or "", text_style)
                    sheet.write(row, 3, m.product_uom_qty, text_style_number)
                    sheet.write(row, 4, ' ', text_style_number)
                    sheet.write(row, 5, saldoawal2, text_style_number)

                if m.location_id in locationstock:
                    saldoawal2 -= m.product_uom_qty
                    totalkeluar += m.product_uom_qty
                    sheet.write(row, 0, number, text_style)
                    sheet.write(row, 1, set_date(m.date), text_style)
                    sheet.write(row, 2, m.picking_id.origin or m.name or "", text_style)
                    sheet.write(row, 3, ' ', text_style_number)
                    sheet.write(row, 4, m.product_uom_qty, text_style_number)
                    sheet.write(row, 5, saldoawal2, text_style_number)

                row += 1
                number += 1
                sheet.write(row, 0, '', text_style)
                sheet.write(row, 1, 'Total', text_style)
                sheet.write(row, 2, '', text_style)
                sheet.write(row, 3, totalmasuk, text_style_number)
                sheet.write(row, 4, totalkeluar, text_style_number)
                sheet.write(row, 5, '', text_style_number)
            # buat formula untuk men-sum / mentotal sales per user
            # sheet.merge_range('A' + str(row + 1) + ':D' + str(row + 1), 'Total', text_style)
            # sheet.write_formula(row, 4, '=SUM(E3:E' + str(row) + ')', number_style)

            # masukkan file excel yang sudah digenerate ke response dan return
            # sehingga browser bisa menerima response dan mendownload file yang sudah digenerate
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        return response
