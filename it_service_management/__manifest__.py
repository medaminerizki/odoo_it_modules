{
    'name': 'IT Service Management',
    'version': '1.0',
    'summary': 'Module for managing IT service tickets',
    'description': 'Custom module for managing IT support tickets in a service company',
    'author': 'Ton Nom',
    'category': 'Services',
    'depends': ['base', 'contacts','it_device'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/service_ticket_report.xml',
        'views/service_ticket_views.xml',
        'views/menu.xml',
        
        
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}
# This file is part of Odoo.