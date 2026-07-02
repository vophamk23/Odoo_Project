{
    'name': "Gate Keeper",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_attendance'],

    'post_init_hook': 'post_init_hook',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/gk_area_warning_type_data.xml',
        'data/scheduler_cron.xml',

        'views/gk_area_views.xml',
        'views/gk_branch_views.xml',
        'views/gate_keeper_views.xml',
        'views/gk_device_model_views.xml',
        'views/gk_access_log_views.xml',
        'views/gk_employee_biometric_views.xml',
        'views/gk_employee_views.xml',
        'views/hr_employee_views.xml',
        'views/gk_controller_sync_views.xml',
        'views/GK_menu.xml'
    ],
}
