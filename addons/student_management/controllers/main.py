from odoo import http
from odoo.http import request
import json


class StudentController(http.Controller):

    @http.route(
        "/api/students", type="http", auth="public", methods=["GET"], csrf=False
    )
    def get_students(self, **kwargs):
        students = request.env["student.student"].sudo().search([])
        data = students.read(["name", "student_id", "gpa", "state"])
        return request.make_response(
            json.dumps(data), headers=[("Content-Type", "application/json")]
        )
