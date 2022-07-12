from odoo import models, fields
  
  
class HrRequireTraining(models.Model):
    _name = 'hr.require.training'
    _description = 'Require Training'

    slide_channel_id = fields.Many2one('slide.channel', required=True, string="Course", help="Required courses for each job position, grade")
    require_hour = fields.Float(string='Required Hours', required=True, default=0.0, help="The minimum number of hours required to reach the course")
    grade_id = fields.Many2one('hr.employee.grade', string='Grade')
    job_id = fields.Many2one('hr.job', string='Job')

    def _prepare_course_line_data(self):
        data = {
            'slide_channel_id': self.slide_channel_id[:1].id,
            'require_hour': sum(self.mapped('require_hour')),
        }
        return data
