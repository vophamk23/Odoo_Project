{
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
