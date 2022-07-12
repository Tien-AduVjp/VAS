from odoo import fields, models


class AssetAssetReport(models.Model):
    _inherit = "asset.asset.report"


    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)

    def _select(self):
        select_str = super(AssetAssetReport, self)._select()
        select_str += """, a.equipment_id as equipment_id,
            equipment.department_id as department_id,
            equipment.employee_id as employee_id"""
        return select_str

    def _from(self):
        from_str = super(AssetAssetReport, self)._from()
        from_str += """left join maintenance_equipment equipment on (a.equipment_id=equipment.id)"""
        return from_str

    def _group_by(self):
        group_by_str = super(AssetAssetReport, self)._group_by()
        group_by_str += """, a.equipment_id, equipment.department_id, equipment.employee_id"""
        return group_by_str
