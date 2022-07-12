from odoo import models, fields
  
  
class HrEmployeeTrainingLine(models.Model):
    _name = 'hr.employee.training.line'
    _description = 'Employee Training Line'

    slide_channel_id = fields.Many2one('slide.channel', required=True, string="Course",
                                       help="Required courses for each job position, grade")
    require_hour = fields.Float(string='Required Hours', required=True, default=0.0,
                        help="The minimum number of hours required to reach the course")
    grade_id = fields.Many2one('hr.employee.grade', string='Grade', related='employee_id.grade_id', readonly=True, store=True)
    job_id = fields.Many2one('hr.job', string='Job', related='employee_id.job_id', readonly=True, store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True, ondelete='cascade', required=True)
