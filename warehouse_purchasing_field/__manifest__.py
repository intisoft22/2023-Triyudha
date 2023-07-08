# -*- coding: utf-8 -*-
{
    'name': 'Purchase Field Module',
    'version': '14.0',
    'summary': 'Purchase Field Module',
    'description': 'Purchase Field Module',
    'author': 'Kevin',
    'website': '',
    'depends': [
        'purchase',
        'stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_field.xml',
        'views/sales_contract.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False
}
