from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    sales_team_manager_ids = fields.One2many('crm.team', 'user_id', string='Sales Team Manager')
    sales_region_manager_ids = fields.One2many('crm.team.region', 'user_id', string='Sales Region Direct Manager')
    sales_region_assistant_ids = fields.Many2many('crm.team.region', 'sale_team_region_users_assistant_rel', 'user_id', 'region_id',
                                                    string='Sales Region Assistant')
