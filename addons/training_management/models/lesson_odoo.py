# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models

# Đã đổi lại thành LessonOdoo thay vì CourseOdoo bị nhầm lúc copy code
class LessonOdoo(models.Model):
    # _name: Tên bảng trong Database
    _name = 'lesson.odoo'
    _description = 'Quản lý Bài học'

    name = fields.Char(string='Tên bài học', required=True)
    is_active = fields.Boolean(string='Trạng thái kích hoạt', copy=False,
                               readonly=True, default=False, help="Bài học này đã mở chưa?")
    
    # fields.Many2one: Mối quan hệ Nhiều-1 (Nhiều Bài học thuộc về 1 Khóa học)
    # comodel_name trỏ tới bảng 'course.odoo'
    parent_id = fields.Many2one(
        comodel_name='course.odoo', string='Thuộc Khoá học nào?')

    def set_is_active_lesson(self):
        # Bật tắt trạng thái giống như bên Khóa học
        for item in self:
            item.is_active = False if item.is_active else True
        return {}
