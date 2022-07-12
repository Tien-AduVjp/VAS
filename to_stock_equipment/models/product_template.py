from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    can_be_equipment = fields.Boolean(string='Can be Equipment', help='To allow link between an equipment and a product', default=False)
    property_default_equipment_category_id = fields.Many2one('maintenance.equipment.category',
                                                 string='Default Equipment Category',
                                                 company_dependent=True,
                                                 help="The default equipment category to put newly created equipment(s) when creating the equipment(s)"
                                                 " from a stock picking.")

    property_maintenance_team_id = fields.Many2one('maintenance.team', string='Maintenance Team',
                                                   company_dependent=True,
                                          help="The default maintenance team for having equipments created from this product during stock transfer")

    technician_user_id = fields.Many2one('res.users', string='Technician')
    equipment_assign_to = fields.Selection(
        [('department', 'Department'), ('employee', 'Employee') , ('other', 'Other')],
        string='Used By')

    @api.constrains('type', 'can_be_equipment', 'tracking')
    def _check_constrain_equipment_tracking(self):
        for r in self:
            if r.can_be_equipment:
                if r.type != 'product':
                    raise ValidationError(_("Product marked with 'Can be Equipment' must be in type of 'Storable Product'."))
                if r.tracking != 'serial':
                    raise ValidationError(_("An equipment product must have 'Tracking By Unique Serial Number' enabled."))

    @api.onchange('can_be_equipment')
    def _onchange_can_be_equipment(self):
        if self.can_be_equipment:
            self.type = 'product'
            self.tracking = 'serial'
        else:
            self.type = self._origin.type or self.type
            self.tracking = self._origin.tracking or self.tracking

    @api.model
    def get_equipment_category(self):
        return self.property_default_equipment_category_id or self.categ_id.property_default_equipment_category_id

    @api.model
    def get_equipment_maintenance_team(self):
        return self.property_maintenance_team_id or self.categ_id.property_maintenance_team_id
