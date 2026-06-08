# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class CourseOdoo(models.Model):
    # _name: Tên bảng trong Database (Odoo sẽ tự động đổi dấu '.' thành dấu '_')
    _name = 'course.odoo'
    # _description: Mô tả ngắn gọn về Model này dùng để hiển thị trong giao diện kỹ thuật
    _description = 'Quản lý Khóa học'

    # Định nghĩa các cột (Trường dữ liệu) trong Database
    # fields.Char: Cột chứa chuỗi văn bản (ví dụ: Tên khóa học)
    name = fields.Char(string='Tên khoá học', required=True)
    
    # fields.Boolean: Cột chứa giá trị Đúng/Sai (True/False)
    is_active = fields.Boolean(string='Trạng thái kích hoạt', copy=False,
                               readonly=True, default=False, help="Khóa học này đã được mở chưa?")
    
    # fields.One2many: Mối quan hệ 1-Nhiều (Một Khóa học có nhiều Bài học)
    lesson_ids = fields.One2many(
        comodel_name='lesson.odoo', inverse_name='parent_id', string='Danh sách Bài học')

    # Hàm Business Logic: Được gọi khi người dùng bấm nút "Active" trên giao diện
    def set_is_active_course(self):
        # self đại diện cho bản ghi (record) hiện tại đang thao tác
        for item in self:
            # Nếu đang là True thì đổi thành False, và ngược lại (Toggle)
            item.is_active = False if item.is_active else True
        return {}
