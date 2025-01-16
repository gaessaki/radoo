{
    'name': 'Radoo'
    'version': '1.0.0',
    'author': 'Radish Cooperative',
    'summary': 'Fast, affordable local delivery with Radish!',
    'category': 'eCommerce',
    'website': 'https://radsish.coop',
    'license': 'GPL-3',
    'depends': ['website_sale', 'sale', 'stock', 'delivery'],
    'data': [
        'views/shipping_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True, 
}