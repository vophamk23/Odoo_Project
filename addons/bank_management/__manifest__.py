{
    "name": "Bank Management",
    "version": "1.0",
    "category": "Accounting",
    "summary": "Quản lý Ngân hàng, Giao dịch, Tài khoản (Premium Edition)",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_view.xml",
        "views/transaction_view.xml",
    ],
    "installable": True,
    "application": True,
}
