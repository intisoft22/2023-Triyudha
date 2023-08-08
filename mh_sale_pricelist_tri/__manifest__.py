# -*- coding: utf-8 -*-
# Copyright (C) 2019-present  Technaureus Info Solutions Pvt. Ltd.(<http://www.technaureus.com/>).

{
    'name': 'Sale Pricelist',
    'version': '14.0.0.0',
    'sequence': 1,
    'category': 'Inventory',
    'summary': 'Sales Pricelist',
    'description': """
""",
    'author': 'Meyrina',
    'website': 'http://www.rexmey.com/',
    'depends': ['sale','mh_warehouse_tri'],
    'data': [
        'security/ir.model.access.csv',
        'views/pricelist_view.xml',
        'views/multipricelist_view.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': True

}
