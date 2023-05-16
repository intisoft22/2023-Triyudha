{
    'name': 'Custom Pricelist',
    'version': '14.0.1.0.0',
    'category': 'Sales',
    'summary': 'Custom Pricelist for Sales',
    'author': 'Gofindo',
    'website': 'https://www.example.com',
    'depends': ['sale', 'base', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/custom_pricelist_views.xml',
        'views/custom_history_pricelist_views.xml',
        'views/product_base_price_views.xml',
        'views/product_price_item_views.xml',
        'views/custom_akses_views.xml',
        'views/menu_views.xml',
        'views/perubahan_pricelist_views.xml',
#         'views/weight_views.xml',
        
    ],
    'installable': True,
    'auto_install': False,
}
