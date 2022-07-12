from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def _default_repair_fee_line_id(self):
        repair_fee_line_id = False
        if self._context.get('default_parent_id'):
            repair_fee_line_id = self.env['project.task'].browse(
                self._context['default_parent_id']).repair_fee_line_id.id
        if not repair_fee_line_id and self._context.get('default_project_id'):
            repair_fee_line_id = self.env['project.project'].browse(
                self._context['default_project_id']).repair_fee_line_id.id
        return repair_fee_line_id

    repair_fee_line_id = fields.Many2one('repair.fee', 'Repair Fee Line',default=_default_repair_fee_line_id,
                                        domain="[('is_service', '=', True), ('order_partner_id', '=', partner_id)]")

    @api.model
    def create(self, values):
        # sub task has the same so line than their parent
        if 'parent_id' in values:
            parent_task = self.env['project.task'].browse(values['parent_id']).sudo()
            if parent_task.repair_fee_line_id:
                values['repair_fee_line_id'] = parent_task.repair_fee_line_id.id
        return super(ProjectTask, self).create(values)

    def write(self, values):
        # sub task has the same so line than their parent
        if 'parent_id' in values:
            parent_task = self.env['project.task'].browse(values['parent_id']).sudo()
            if parent_task.repair_fee_line_id:
                values['repair_fee_line_id'] = parent_task.repair_fee_line_id.id

        result = super(ProjectTask, self).write(values)
        # reassign SO line on related timesheet lines
        if 'repair_fee_line_id' in values:
            # subtasks should have the same SO line than their mother
            self.sudo().mapped('child_ids').write({
                'ro_line': values['repair_fee_line_id']
            })
            self.sudo().mapped('timesheet_ids').write({
                'ro_line': values['repair_fee_line_id']
            })
        return result

    def unlink(self):
        if any(task.repair_fee_line_id for task in self):
            raise ValidationError(
                _('You cannot delete a task related to a Repair Order. You can only archive this task.'))
        return super(ProjectTask, self).unlink()

    def action_view_ro(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "repair",
            "views": [[False, "form"]],
            "res_id": self.repair_fee_line_id.repair_id.id,
            "context": {"create": False, "show_sale": True},
        }

