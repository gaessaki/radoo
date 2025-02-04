{
    'name': 'Radoo',
    'version': '1.0.0',
    'author': 'Radish Cooperative',
    'summary': 'Fast, affordable local delivery with Radish!',
    'category': 'eCommerce',
    'website': 'https://radish.coop',
    'depends': ['website_sale', 'sale', 'stock', 'delivery', 'base'],
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