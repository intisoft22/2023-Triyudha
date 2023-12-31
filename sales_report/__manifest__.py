# -*- coding: utf-8 -*-
{
    'name': 'Sales Report',
    'version': '14.0',
    'summary': 'Sales Report',
    'description': 'Faktur Penjualan, Laporan Piutang, Register Pembelian',
    'author': 'Mifta',
    'website': '',
    'depends': [
        'sale',
        'account',
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/faktur_penjualan_view.xml',
        'wizard/register_penjualan_view.xml',
        'wizard/laporan_piutang_view.xml',
        'views/sales.xml',
        'report/report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False
}
