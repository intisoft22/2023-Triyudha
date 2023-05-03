# -*- coding: utf-8 -*-
# Copyright (C) 2019-present  Technaureus Info Solutions Pvt. Ltd.(<http://www.technaureus.com/>).

{
    "name": "Production for Triyudha",
    "summary": "Production for Triyudha",
    "version": "14.0",
    "author": "Meyrina Herawati",
    "category": "Production Management",
    'depends': ['stock','mh_warehouse_tri','stock_request','stock_request_submit','web_domain_field','mrp'],
    'data': [
        'security/ir.model.access.csv',
        'security/security_data.xml',
        'views/stock_request_type_view.xml',
        'views/stock_request_view.xml',
        'views/stock_request_order_submit_views.xml',
        'views/stock_request_order_warehouse_views.xml',
        'views/stock_request_order_prod_views.xml',
        'views/stock_picking_view.xml',


    ],
    'installable': True,
    'auto_install': True,
    'application': True

}
