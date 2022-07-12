from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    asset_status = fields.Selection([
        ('draft', 'Draft'), ('open', 'Running'), ('stock_in', 'Stock-In'), ('sold', 'Sold'), ('disposed', 'Disposed'), ('close', 'Close')],
        string='Asset Status', readonly=True)

    @api.model
    def _prepare_equipment_assignment_vals(
            self,
            asset_status=None,
            assign_to=False,
            department=False,
            employee=False,
            assign_date=False
            ):

        vals = {
            'equipment_assign_to': assign_to or 'employee',
            'employee_id': employee.id if employee else False,
            'department_id': department.id if department else False,
            'assign_date': assign_date,
            }

        if asset_status is not None:
            vals['asset_status'] = asset_status
        return vals
