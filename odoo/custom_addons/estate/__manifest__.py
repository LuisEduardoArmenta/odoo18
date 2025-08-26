{
    'name': 'Estate',
    'version': '1.0',
    'summary': 'Real estate advertisement',
    'description': '''
        Real Estate Management System
        =============================
        
        This module provides a complete real estate management system with:
        * Property listings management
        * Property types and tags
        * Advanced search and filtering
        * Property status tracking
        * Salesperson and buyer management
        * Real estate agent management
        * Performance analytics and dashboards
        
        Features:
        * Kanban, List and Form views
        * Property validations and constraints
        * Computed fields for areas and deadlines
        * Onchange methods for user experience
        * Beautiful UI with colors and decorations
        * Advanced widgets and sprinkles
        * Market analysis and reporting
    ''',
    'category': 'Real Estate',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'data': [
        'security/ir.model.access.csv',
        'security/estate_security.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_offer_views.xml',
        'views/res_partner_views_clean.xml',
        'views/estate_property_sprinkles.xml',
        'views/estate_commission_views.xml',
        'reports/estate_reports.xml',
        'data/estate_demo.xml',
        'data/estate_demo_agents.xml',
    ],
    'demo': [
        'data/estate_demo.xml',
    ],
}
