# -*- coding: utf-8 -*-
{
    'name': 'Accounting Excel Report',
    'version': '14.0',
    'summary': 'Accounting Excel Report',
    'description': 'Accounting Excel Report',
    'author': 'Kevin',
    'website': '',
    'depends': [
        'account',
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/cash_bank_view.xml',
        'views/accounting.xml',
        'report/report.xml'


    ],
    'installable': True,
    'auto_install': False,
    'application': False
}
