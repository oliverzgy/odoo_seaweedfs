# -*- coding: utf-8 -*-
{
    'name': "Odoo SeaweedFS",

    'summary': """
        Odoo SeaweedFS""",

    'description': """
        Odoo SeaweedFS       
    """,

    'author': "Zhiguo Yuan",
    'email': "oliver.yuan@openstone.cn",
    'website': "http://www.openstone.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','base_automation'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/base_automation.xml',
        'views/views.xml',
        'views/templates.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}