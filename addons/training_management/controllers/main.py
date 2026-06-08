# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import json
from urllib.parse import urlparse, parse_qs

import requests
from werkzeug import urls
from werkzeug.exceptions import Forbidden
from werkzeug.utils import redirect

from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.tools import html_escape

_logger = logging.getLogger(__name__)


# Kế thừa từ http.Controller để biến class này thành bộ điều hướng (Router) cho Website
class MainController(http.Controller):

    # @http.route: Định nghĩa đường dẫn URL trên trình duyệt
    # type='http': Trả về trang web HTML bình thường (không phải JSON/API)
    # auth="user": Bắt buộc người dùng phải đăng nhập mới được xem
    @http.route('/courses', type='http', auth="user", website=True)
    def get_courses(self):
        # http.request.env: Giống như self.env ở phần Model, dùng để tương tác với Database
        # .search([]): Lấy toàn bộ danh sách Khóa học
        records = http.request.env['course.odoo'].search([])

        # render: Ghép dữ liệu vừa lấy được vào file giao diện XML để tạo ra trang web
        return http.request.render(
            # Tên template XML (Khai báo trong thư mục views)
            "training_management.course_list_template",

            # Truyền dữ liệu vào template
            {"courses": records},
        )
