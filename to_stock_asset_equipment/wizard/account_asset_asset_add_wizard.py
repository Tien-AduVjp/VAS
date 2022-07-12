from odoo import api, fields, models


class AccountAssetAssetAddWizard(models.TransientModel):
    _inherit = 'account.asset.asset.add.wizard'
    
    
    asset_assign_to = fields.Selection([('department', 'Department'), ('employee', 'Employee'), ('other', 'Other')], 
                                           string='Used By')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string='Department')
    
    @api.onchange('asset_assign_to', 'employee_id', 'department_id')
    def _onchange_asset_assign_by(self):
        if not self.asset_assign_to:
            self.employee_id = False
            self.department_id = False
        elif self.asset_assign_to == 'department':
            self.employee_id = False
        elif self.asset_assign_to == 'employee':
            self.department_id = False
    
    def _prepare_production_lot(self):
        self.ensure_one()
        vals = {}
        if self.asset_assign_to:
            vals.update({
                'asset_assign_to': self.asset_assign_to,
                })
        if self.employee_id:
            vals.update({
                'employee_id': self.employee_id.id,
            })
        if self.department_id:
            vals.update({
                'department_id': self.department_id.id,
            })
        return vals
    
    def _update_account_asset_vals(self, asset_id):
        super(AccountAssetAssetAddWizard, self)._update_account_asset_vals(asset_id)
        lot_id = asset_id.production_lot_id
        lot_vals = self._prepare_production_lot()
        if lot_id and lot_vals:
            can_write = lot_id.check_access_rights('write', False)
            lot_id = can_write and lot_id or lot_id.sudo()
            lot_id.write(lot_vals)
        
        