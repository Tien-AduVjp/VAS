from odoo import models, fields, api
 

class Project(models.Model):
    _inherit = 'project.project'    
   
    department_id = fields.Many2one('hr.department',
        compute='_compute_deparment', 
        string='Department', 
        store=True,        
        readonly=False, 
        help='The department that is responsible for this project'
    )    
    # TODO: remove `timesheet_ids` in master/14+ as this field is already in core since Odoo 14
    timesheet_ids = fields.One2many('account.analytic.line','project_id','Associated Timesheets')
    associated_department_ids = fields.Many2many(
        'hr.department',
        'project_associated_hr_department_rel',
        'project_id',
        'department_id',
        string='Involving Departments',
        compute='_compute_involve_deparment',
        store=True,
        readonly=False,
        help='The associated departments whose employees involve this project via timesheet entries on the project and its tasks.'
    )    

    @api.depends('user_id')
    def _compute_deparment(self):
        for r in self:
            r.department_id = r.user_id.employee_id.department_id

    @api.depends('timesheet_ids.employee_id')
    def _compute_involve_deparment(self):
        for r in self:
            r.associated_department_ids = [(6,0,r.timesheet_ids.employee_id.department_id.ids)]  
                      