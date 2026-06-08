from odoo import models, fields

class Course(models.Model):
    _name = "student.course"
    _description = "Khóa học"
    
    name = fields.Char(string="Tên khóa học", required=True)
    code = fields.Char(string="Mã khóa học", required=True)
    credits = fields.Integer(string="Số tín chỉ", default=3)
    
    # Quan hệ Nhiều-Nhiều ngược lại tới student.student
    student_ids = fields.Many2many("student.student", string="Sinh viên tham gia")
