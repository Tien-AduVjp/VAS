from odoo import models, fields
  
  
class Job(models.Model):
    _inherit = 'hr.job'

    require_training_ids = fields.One2many('hr.require.training', 'job_id', string='Required Courses')
