from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    asset_assign_to = fields.Selection([('department', 'Department'), ('employee', 'Employee'), ('other', 'Other')],
                                       string='Used By', groups='maintenance.group_equipment_manager')
    employee_id = fields.Many2one('hr.employee', string='Employee', groups='maintenance.group_equipment_manager')
    department_id = fields.Many2one('hr.department', string='Department', groups='maintenance.group_equipment_manager')

    def _action_done(self):
        """ This method is called during a move's `action_done`. It'll actually move a quant from
        the source location to the destination location, and unreserve if needed in the source
        location.

        This method is intended to be called on all the move lines of a move. This method is not
        intended to be called when editing a `done` move (that's what the override of `write` here
        is done.
        """
        res = super(StockMoveLine, self)._action_done()

        for r in self.exists().filtered(lambda r: r.lot_id.sudo().equipment_id):
            vals = r.lot_id.sudo().equipment_id._prepare_equipment_assignment_vals(
                assign_to=r.asset_assign_to,
                employee=r.employee_id if r.asset_assign_to != 'department' else False,
                department=r.department_id if r.asset_assign_to != 'employee' else False
                )
            if r.asset_assign_to:
                vals['assign_date'] = r.date
            r.lot_id.sudo().equipment_id.write(vals)
        return res
