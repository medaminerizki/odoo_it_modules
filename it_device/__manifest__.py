# -*- coding: utf-8 -*-

{
    'name': 'IT Device',
    'version': '1.1',
    'author': 'Mohamed Amine Rizki',
    'sequence': 110,
    'summary': 'IT Devices, Manage IT Devices and specifications',
    'license': 'OPL-1',
    'description': """
IT Device Management
==================================
This module supports the management and storage of IT equipment in the company.
From now on, control over moved devices and their specifications is much easier. You get the possibility of gathering computers, phones and other IT devices in one place. Each group of devices has its own specification and technical data. Moreover, in the employee card a new page "Equipment" appears, where you can see the equipment owned by the employee. This module should only be operated by employees assigned to this task. Unauthorized people should not be able to access it.

Main features
-------------
* Add computers.
* Add phones
* Add other devices
* Managing and storing IT device specifications
* Manage equipment transfers
* Generate protocols
* Device overview
* Database of models, processors, mobile networks, device types

""",
    'category': 'Human Resources',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/it_device_security.xml',
        'security/ir.model.access.csv',
        'views/it_device_view.xml',
        'data/it_device_demo.xml',
        'views/it_device_brands.xml',
        'views/hr_employee_inherited_view.xml',
        
        
    ],
    'images': ['static/description/it_dev.jpg'],
    'auto_install': False,
    'application': True,
    'installable': True,
}