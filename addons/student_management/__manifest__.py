{
    "name": "Student Management",
    "version": "1.0",
    "category": "Education",
    "summary": "Quản lý sinh viên đơn giản",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/student_view.xml",
        "views/course_view.xml",
    ],
    "installable": True,
    "application": True,
}
