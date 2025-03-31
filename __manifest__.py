{
    'name': 'Radoo',
    'version': '15.0.0.1',
    'author': 'Radish Cooperative',
    'summary': 'Fast, affordable local delivery with Radish!',
    'category': 'eCommerce',
    'website': 'https://radish.coop',
    'external_dependencies': {
        'python': ['html2text']
    },
    'depends': ['stock', 'delivery'],
    'data': [
        'views/delivery_carrier_view.xml',
        'views/stock_picking_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'radoo/static/src/css/radish_button.css',
        ],
    },
    'installable': True, 
    'application': True,
    'license': 'GPL-3',
}