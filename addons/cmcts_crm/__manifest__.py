{
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
