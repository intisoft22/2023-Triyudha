# -*- coding: utf-8 -*-
{
    'name': 'Accounting Module Report',
    'version': '14.0',
    'summary': 'Accounting Module Report',
    'description': 'Accounting Module Report',
    'author': 'Kevin',
    'website': '',
    'depends': [
        'account',
        'report_xlsx'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/accounting.xml',
        'report/report.xml',
        'report/bukti_bank_masuk_template.xml',
        'report/bukti_bank_keluar_template.xml',
        'report/bukti_kas_masuk_template.xml',
        'report/bukti_kas_keluar_template.xml',
        'wizard/rincian_kas_bank_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False
}
