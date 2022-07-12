from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.model
    def _get_default_maintenance_team(self):
        maintenance_team = self.sudo().env.ref('maintenance.equipment_team_maintenance')
        if maintenance_team and (not maintenance_team.company_id or maintenance_team.company_id == self.env.company):
            return maintenance_team
        return False

    property_default_equipment_category_id = fields.Many2one('maintenance.equipment.category',
                                                 string='Default Equipment Category',
                                                 company_dependent=True,
                                                 help="The default equipment category to put newly created equipment(s) when creating the equipment(s)"
                                                 " from a stock picking. This parameter can be overridden on the product configuration.")

    property_maintenance_team_id = fields.Many2one('maintenance.team', string='Maintenance Team',  default=_get_default_maintenance_team,
                                                   company_dependent=True,
                                                   help="The default maintenance team for equipments created from a product of this product category")

    technician_user_id = fields.Many2one('res.users', string='Technician')
    equipment_assign_to = fields.Selection(
        [('department', 'Department'), ('employee', 'Employee') , ('other', 'Other')],
        string='Used By',
        required=True,
        default='employee')
