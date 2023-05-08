# -*- coding: utf-8 -*-
# Copyright (C) 2019-present  Technaureus Info Solutions Pvt. Ltd.(<http://www.technaureus.com/>).

{
    'name': 'Stock Card',
    'version': '12.0.0.0',
    'sequence': 1,
    'category': 'Inventory',
    'summary': 'Stock Card',
    'description': """
""",
    'author': 'Meyrina',
    'website': 'https://www.innotek.co.id/',
    'depends': ['stock','mh_warehouse_tri'],
    'data': [
        'security/security_data.xml',
        'security/ir.model.access.csv',
        'views/stock_card_view.xml',
        'reports/views/inventory_card_report_view.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': True

}
