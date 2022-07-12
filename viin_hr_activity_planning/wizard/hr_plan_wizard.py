from odoo import models


class HrPlanWizard(models.TransientModel):
    _inherit = 'hr.plan.wizard'

    def action_launch(self):
        res = super(HrPlanWizard, self).action_launch()
        for activity_type in self.plan_id.plan_activity_type_ids:
            responsible = activity_type.get_responsible_id(self.employee_id)

            date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type.activity_type_id)
            if not self.env['hr.employee'].with_user(responsible).check_access_rights('read', raise_exception=False):
                employee_activities = self.env['mail.activity'].with_context({'mail_activity_quick_update': True}).create({
                    'res_id': self.employee_id.id,
                    'res_model_id': self.env['ir.model']._get('hr.employee').id,
                    'summary': activity_type.summary,
                    'note': activity_type.note,
                    'activity_type_id': activity_type.activity_type_id.id,
                    'user_id': responsible.id,
                    'date_deadline': date_deadline,
                    'automated': True
                })

                tmp_activities = employee_activities.sudo().copy(default={
                    'res_model_id': self.env['ir.model']._get('hr.employee.public').id,
                })
                tmp_activities.action_notify()

        return res
