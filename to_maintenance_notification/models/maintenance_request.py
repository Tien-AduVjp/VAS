from datetime import timedelta

from odoo import models, fields, api


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    days_to_notify = fields.Integer(string='Days to Notify', related='equipment_id.days_to_notify', readonly=True, store=True)

    date_to_notify = fields.Date(string='Date to notify', compute='_compute_date_to_notify', store=True,
                                 help="Technical field that indicated the date on which the notification should be sent.")

    maintenance_milestone_id = fields.Many2one('product.milestone', string='Maintenance Milestone')

    notified = fields.Boolean(string='Notified', default=False)

    @api.depends('schedule_date', 'days_to_notify')
    def _compute_date_to_notify(self):
        for r in self:
            if r.schedule_date and r.days_to_notify:
                date_to_notify = fields.Date.to_date(r.schedule_date) - timedelta(days=r.days_to_notify)
                r.date_to_notify = date_to_notify

    def cron_notify_maintenance(self):
        today = fields.Date.today()
        maintenance_requests = self.search([('date_to_notify', '<=', today), ('stage_id.done', '!=', True), ('notified', '=', False)])
        maintenance_requests.action_send_notification()

    def action_send_notification(self):
        email_template = self.env.ref('to_maintenance_notification.maintenance_request_mail_template_notify')
        for r in self:
            r.notified = True
            r.message_post_with_template(email_template.id)

    def action_view_maintenance_schedule_list(self):
        maintenance_schedules = self.equipment_id.maintenance_schedule_ids.filtered(lambda l: l.product_milestone_id.id == self.maintenance_milestone_id.id)
        if len(maintenance_schedules):
            action = self.env['ir.actions.act_window']._for_xml_id('to_product_maintenance_schedule.maintenance_schedule_list_view')
            action['domain'] = [('id', 'in', maintenance_schedules.ids)]
            action['context'] = {'create': False}
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
