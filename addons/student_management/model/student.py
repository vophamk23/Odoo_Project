from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Student(models.Model):
    _name = "student.student"
    _description = "Sinh viên"
    _rec_name = "student_id"
    _order = "student_id"

    # Fields
    name = fields.Char(string="Họ tên", required=True)
    student_id = fields.Char(string="MSSV", required=True)
    email = fields.Char(string="Email")
    birth_date = fields.Date(string="Ngày sinh")
    gpa = fields.Float(string="GPA")
    state = fields.Selection(
        [
            ("active", "Đang học"),
            ("graduated", "Đã tốt nghiệp"),
            ("suspended", "Bảo lưu"),
        ],
        default="active",
        string="Trạng thái",
    )
    course_ids = fields.Many2many(
        "student.course",
        string="Khóa học đã đăng ký"
    )

    # Computed field (tự tính)
    age = fields.Integer(string="Tuổi", compute="_compute_age", store=True)

    @api.depends("birth_date")
    def _compute_age(self):
        from datetime import date

        for rec in self:
            if rec.birth_date:
                rec.age = date.today().year - rec.birth_date.year
            else:
                rec.age = 0

    # Constraint (ràng buộc)
    @api.constrains("gpa")
    def _check_gpa(self):
        for rec in self:
            if not (0.0 <= rec.gpa <= 4.0):
                raise ValidationError("GPA phải từ 0.0 đến 4.0!")

    # Override create (hook khi tạo mới)
    @api.model
    def create(self, vals):
        record = super().create(vals)
        # Gửi email hoặc log ở đây
        return record
