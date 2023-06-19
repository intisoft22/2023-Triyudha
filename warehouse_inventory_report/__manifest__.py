# -*- coding: utf-8 -*-
{
    'name': 'Inventory Module',
    'version': '14.0',
    'summary': 'Inventory Module',
    'description': 'Inventory Module',
    'author': 'Kevin',
    'website': '',
    'depends': [
        'stock',
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/kartu_stock_view.xml',
        'views/inventory.xml',
        'report/report.xml',
        'report/serah_terima_template.xml'

    ],
    'installable': True,
    'auto_install': False,
    'application': False
}
