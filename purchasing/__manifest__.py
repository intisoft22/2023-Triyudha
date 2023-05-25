# -*- coding: utf-8 -*-
{
    'name': 'Purchasing Module',
    'version': '14.0',
    'summary': 'Purchasing Module',
    'description': 'Purchasing Module',
    'author': 'Mifta',
    'website': '',
    'depends': [
        'purchase',
        'web_domain_field',
        'stock',
        'report_xlsx',
        'stock_picking_invoicing',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/register_pembelian_view.xml',
        'wizard/kartu_hutang_view.xml',
        'views/purchase.xml',
        'report/report.xml',
        'report/purchase_order_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False
}
