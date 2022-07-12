from odoo import fields, models


class Project(models.Model):
    _inherit = 'project.project'
    
    user_technician_id = fields.Many2one('res.users', 
         string='Lead Technician',
         help="Tech Lead is the promoted user that has permission to read the sales order and sales order lines of the related project"
    )
