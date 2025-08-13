{
    'name': 'Estate',
    'version': '1.0',
    'summary': 'Real estate advertisement',
    'category': 'Real Estate',
    'depends': ['base'],
    'application': True,  # hace que se vea en App list
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
    ],
}
