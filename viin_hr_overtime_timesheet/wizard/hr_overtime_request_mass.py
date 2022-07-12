from odoo import models, fields, api


class HrOvertimeRequestMass(models.TransientModel):
    _inherit = 'hr.overtime.request.mass'

    for_project_id = fields.Many2one('project.project', string='Project', help="The project for which this overtime plan is")
    project_required = fields.Boolean(related='reason_id.project_required')
    

            
