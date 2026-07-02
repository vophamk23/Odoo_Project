from . import models
from . import utils


def post_init_hook(env):
    hr_employees = env['hr.employee'].search([])
    gk_employee_env = env['t4.gate_keeper.employee']
    
    for emp in hr_employees:
        gk_employee_env.create({
            'name': emp.name,
            'emp_id': emp.emp_id,
            'hr_employee_id': emp.id,
        })
