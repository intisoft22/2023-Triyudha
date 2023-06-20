# -*- coding: utf-8 -*-
{
    'name': 'Report Kartu Persediaan Inventory',
    'version': '14.0',
    'summary': 'Report Kartu Persediaan Inventory',
    'description': 'Report Kartu Persediaan Inventory',
    'author': 'Mifta',
    'website': '',
    'depends': [
        'product',
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/kartu_persediaan_view.xml',
        'views/inventory.xml',
        'report/report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False
}
