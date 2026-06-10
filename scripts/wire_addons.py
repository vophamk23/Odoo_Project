import os

base_path = r'c:\Users\ASUS\Desktop\VoPC-cmcts\addons'

manifests = {
    'cmcts_inventory': """{
    'name': 'CMCTS Inventory Customization',
    'version': '1.0',
    'summary': 'Quản lý kho bắt buộc nhập Serial Number',
    'author': 'Phase1-team',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
}
""",
    'cmcts_crm': """{
    'name': 'CMCTS CRM Customization',
    'version': '1.0',
    'summary': 'Quản lý phễu CRM và nhắc việc tự động',
    'author': 'Phase1-team',
    'depends': ['crm', 'mail'],
    'data': [
        'data/crm_stage_data.xml',
        'data/automation_rules.xml',
        'data/mail_templates.xml',
    ],
    'installable': True,
    'application': False,
}
""",
    'cmcts_website': """{
    'name': 'CMCTS Website',
    'version': '1.0',
    'summary': 'Giao diện Website và Form tư vấn đổ về CRM',
    'author': 'Phase1-team',
    'depends': ['website', 'crm'],
    'data': [
        'views/homepage_templates.xml',
        'views/contact_form_templates.xml',
    ],
    'installable': True,
    'application': True,
}
"""
}

inits = {
    'cmcts_inventory/__init__.py': "from . import models\n",
    'cmcts_inventory/models/__init__.py': "from . import stock_picking\nfrom . import product_template\n",
    'cmcts_crm/__init__.py': "from . import models\n",
    'cmcts_crm/models/__init__.py': "from . import crm_lead\n",
    'cmcts_website/__init__.py': "from . import controllers\n",
    'cmcts_website/controllers/__init__.py': "from . import main\n",
}

for module, content in manifests.items():
    with open(os.path.join(base_path, module, '__manifest__.py'), 'w', encoding='utf-8') as f:
        f.write(content)

for path, content in inits.items():
    normalized_path = path.replace('/', '\\')
    with open(os.path.join(base_path, normalized_path), 'w', encoding='utf-8') as f:
        f.write(content)

print("Wiring done!")
