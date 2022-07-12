from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    
    
    asset_assign_to = fields.Selection([('department', 'Department'), ('employee', 'Employee'), ('other', 'Other')], 
                                           string='Used By', groups='maintenance.group_equipment_manager', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', groups='maintenance.group_equipment_manager', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', groups='maintenance.group_equipment_manager', tracking=True)
    
    @api.onchange('asset_assign_to')
    def _onchange_asset_assign_by(self):
        if self.asset_assign_to == 'other':
            self.employee_id = False
            self.department_id = False
        elif self.asset_assign_to == 'department':
            self.employee_id = False
        elif self.asset_assign_to == 'employee':
            self.department_id = False
    
    def _prepare_production_lot_vals_when_removing_asset(self, status=False):
        self.ensure_one()
        res = super(StockProductionLot, self)._prepare_production_lot_vals_when_removing_asset(status)
        
        res.update({
            'asset_assign_to': False,
            'employee_id': False,
            'department_id': False,
            })
        return res
    
    def _update_equipment_information_val(self):
        for r in self:
            if r.equipment_id:
                vals = {
                    'asset_status': r.asset_status,
                    }
                if r.asset_assign_to:
                    vals.update({
                    'equipment_assign_to': r.asset_assign_to,
                    'employee_id': r.employee_id.id,
                    'department_id': r.department_id.id,
                    })
                equipment = r.equipment_id.check_access_rights('write', False) and r.equipment_id or r.equipment_id.sudo()
                equipment.write(vals)

    @api.model
    def create(self, vals):
        res = super(StockProductionLot, self).create(vals)
        if 'asset_assign_to' in vals or 'asset_status' in vals:
            res._update_equipment_information_val()
        return res
    
    def write(self, vals):
        res = super(StockProductionLot, self).write(vals)
        if any(arg in vals for arg in ['asset_assign_to', 'asset_status','employee_id']):
            self._update_equipment_information_val()
        return res
