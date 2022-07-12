from odoo import fields, models


class AssetAssetReport(models.Model):
    _inherit = "asset.asset.report"


    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)

    def _select(self):
        select_str = super(AssetAssetReport, self)._select()
        select_str += """, a.equipment_id as equipment_id, lot.employee_id as employee_id, lot.department_id as department_id """
        return select_str

    def _group_by(self):
        group_by_str = super(AssetAssetReport, self)._group_by()
        group_by_str += """, a.equipment_id, lot.employee_id, lot.department_id """
        return group_by_str
    
