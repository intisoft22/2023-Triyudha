# -*- coding: utf-8 -*-
{
    'name': 'Sales Module',
    'version': '14.0',
    'summary': 'Sales Module',
    'description': 'Sales Module',
    'author': 'Kevin',
    'website': '',
    'depends': [
        'sale',
        'sale_management'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sales.xml',
        'report/report.xml',
        'report/order_pembelian_template.xml',
        'report/surat_jalan_template.xml',
        'report/invoice_template.xml',
        'report/kwitansi_template.xml'

    ],
    'installable': True,
    'auto_install': False,
    'application': False
}