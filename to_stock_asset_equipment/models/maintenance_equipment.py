from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    
    
    asset_status = fields.Selection([
        ('draft', 'Draft'), ('open', 'Running'), ('stock_in', 'Stock-In'), ('sold', 'Sold'), ('disposed', 'Disposed'), ('close', 'Close')], 
        string='Asset Status', default='draft', readonly=True)

    @api.model
    def _prepare_equipment_vals_when_removing_asset(self):
        return {
            'asset_status': False,
            'employee_id': False,
            'department_id': False,
            'assign_date': False,
            }        
