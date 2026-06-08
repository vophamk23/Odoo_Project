{
    # Tên hiển thị của ứng dụng trên giao diện Odoo
    "name": "Hệ Thống Quản Lý Thư Viện (Library Management)",
    
    # Mô tả ngắn gọn xuất hiện dưới tên ứng dụng
    "summary": "Ứng dụng quản lý Sách và Thư viện",
    
    # Mô tả chi tiết khi bấm vào xem thông tin ứng dụng
    "description": """
    ====================
    Ứng dụng Quản lý Thư viện cơ bản:
    - Quản lý danh sách đầu sách
    - Phân loại sách
    - Thông tin Tác giả / Nhà xuất bản
    ====================
    """,
    "author": "Nguyen The Vy",
    "website": "https://github.com/vyngt/odoo-sample-app",
    
    # Nhóm danh mục của ứng dụng trong kho Apps
    "category": "Services/Library",
    "version": "17.0.1.0.0",
    
    # Danh sách các module bắt buộc phải cài đặt trước khi cài module này
    "depends": ["base"],
    
    # Khai báo các file giao diện (XML), bảo mật (CSV), báo cáo sẽ được load vào hệ thống
    "data": [
        "security/tutorial_security.xml",     # File định nghĩa các nhóm quyền (Groups)
        "security/ir.model.access.csv",       # File cấp quyền CRUD cho từng nhóm trên từng bảng (Models)
        "views/book_view.xml",                # File thiết kế giao diện Form, Tree, Search cho Sách
        "views/menu.xml",                     # File thiết kế thanh Menu chính và Menu con
        "views/book_list_template.xml",       # File giao diện cho Website (Frontend)
        "reports/tutorial_library_book_report.xml",
        "reports/library_publisher_report.xml",
    ],
    
    # application = True báo hiệu đây là một ứng dụng chính (App), không phải là module ẩn
    "application": True,
    
    # Dữ liệu mẫu (Demo data) sẽ được load nếu check vào ô "Load Demo Data" khi cài DB
    "demo": [
        "data/res.partner.csv",
        "data/tutorial.library.book.csv",
        "data/book_demo.xml",
    ],
}
