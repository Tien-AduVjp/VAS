from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    equipment_working_frequency_ids = fields.One2many('equipment.working.frequency', 'equipment_id', string='Working Frequency')

    @api.onchange('effective_date')
    def _onchange_effective_date(self):
        self.equipment_working_frequency_ids._compute_total_working_amount()

    @api.constrains('equipment_working_frequency_ids')
    def _check_working_frequency_ids(self):
        for r in self:
            uom_categ_ids = r.equipment_working_frequency_ids.mapped('working_uom_id.category_id')
            if len(uom_categ_ids) < len(r.equipment_working_frequency_ids):
                raise ValidationError(_("Cannot set working frequency with the same Unit of Measure category in one product."))
