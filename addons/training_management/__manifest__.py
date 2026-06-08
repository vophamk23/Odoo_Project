{
    # Tên module hiển thị trên màn hình Ứng dụng
    'name': 'Hệ Thống Quản Lý Đào Tạo (LMS)',
    'version': '1.0',

    # Loại module (Category) giúp lọc dễ hơn trong Apps
    'category': 'Education',

    # Độ ưu tiên (sequence): Số càng nhỏ thì ứng dụng càng xếp lên đầu
    'sequence': 5,

    # Tóm tắt ngắn và mô tả dài về ứng dụng
    'summary': 'Ứng dụng quản lý Khóa học và Bài học chuyên nghiệp',
    'description': 'Giúp trung tâm đào tạo quản lý danh sách Khóa học, Bài học và trạng thái kích hoạt.',


    # Module dựa trên các category nào
    # Khi hoạt động, category trong 'depends' phải được install
    ### rồi module này mới đc install
    'depends': [],

    # Module có được phép install hay không
    # Nếu bạn thắc mắc nếu tắt thì làm sao để install
    # Bạn có thể dùng 'auto_install'
    'installable': True,
    'auto_install': False,
    'application': True,

    # Import các file cấu hình
    # Những file ảnh hưởng trực tiếp đến giao diện (không phải file để chỉnh sửa giao diện)
    ## hoặc hệ thống (file group, phân quyền)
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/course_list_template.xml',
        'views/menu_item_course.xml',
        'views/menu_item_lesson.xml',
        'views/menu_view.xml',
    ],

    # Import các file cấu hình (chỉ gọi từ folder 'static')
    # Những file liên quan đến
    ## + các class mà hệ thống sử dụng
    ## + các chỉnh sửa giao diện
    ## + t
    'assets': {
        'point_of_sale._assets_pos': [
            'training_management/static/src/**/*'
        ],

    },
    'license': 'LGPL-3',
}
