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
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/faktur_penjualan_view.xml',
        'views/sales.xml',
        'report/report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False
}
