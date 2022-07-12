from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Hours',
                                            default=lambda self: self.env.company.resource_calendar_id,
                                            domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    equipment_working_frequency_ids = fields.One2many('equipment.working.frequency', 'equipment_id', string='Working Frequency', copy=True)

    @api.constrains('equipment_working_frequency_ids')
    def _check_working_frequency_ids(self):
        for r in self:
            uom_categ_ids = r.equipment_working_frequency_ids.mapped('working_uom_id.category_id')
            if len(uom_categ_ids) < len(r.equipment_working_frequency_ids):
                raise ValidationError(_("Cannot set working frequency with the same Unit of Measure category in one product."))
