from odoo import models, fields, api


class HelpdeskTicketSLA(models.Model):
    _name = 'helpdesk.sla.line'
    _description = 'SLA Status'
    _order = 'deadline_datetime ASC'
    _rec_name = 'sla_id'

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', required=True, ondelete='cascade', index=True)
    sla_id = fields.Many2one('helpdesk.sla', string='SLA', required=True, ondelete='cascade')
    deadline_datetime = fields.Datetime(string='Deadline', compute='_compute_deadline', store=True)
    reached_datetime = fields.Datetime(string='Reached Date', compute='_compute_reached_datetime', store=True, help="Date and time at which the SLA stage was reached")
    status = fields.Selection([('failed', 'Failed'), ('reached', 'Reached'), ('ongoing', 'Ongoing')], string='Status', compute='_compute_status', store=True)
    exceeded_days = fields.Float(string='Exceeded Working Days', compute='_compute_exceeded_time', store=True, help="Working days exceeded for reached SLAs compared with deadline.")

    @api.depends('ticket_id.create_date', 'sla_id')
    def _compute_deadline(self):
        for r in self:
            deadline = r.ticket_id.create_date
            working_calendar = r.ticket_id.team_id.resource_calendar_id

            if working_calendar and deadline:
                r.deadline_datetime = working_calendar.plan_hours(r.sla_id.time_hours, deadline, compute_leaves=True)
            else:
                r.deadline_datetime = deadline

    @api.depends('ticket_id.stage_id')
    def _compute_reached_datetime(self):
        for r in self:
            stage_ids = r.ticket_id.team_id.stage_ids.ids
            if r.sla_id.stage_id == r.ticket_id.stage_id:
                r.reached_datetime = fields.Datetime.now()
            else:
                if stage_ids.index(r.ticket_id.stage_id.id) > stage_ids.index(r.sla_id.stage_id.id) and not r.reached_datetime:
                    reached_datetime = r.ticket_id.sla_line_ids.filtered(lambda s: s.sla_id.stage_id == r.ticket_id.stage_id)[:1].reached_datetime
                    r.reached_datetime = reached_datetime or fields.Datetime.now()
                elif stage_ids.index(r.ticket_id.stage_id.id) > stage_ids.index(r.sla_id.stage_id.id) and r.reached_datetime:
                    r.reached_datetime = r.reached_datetime
                else:
                    r.reached_datetime = False

    @api.depends('deadline_datetime', 'reached_datetime')
    def _compute_status(self):
        for r in self:
            if r.reached_datetime and r.deadline_datetime:
                r.status = r.reached_datetime < r.deadline_datetime and 'reached' or 'failed'
            elif r.reached_datetime:
                r.status = 'ongoing'
            else:
                r.status = (not r.deadline_datetime or r.deadline_datetime > fields.Datetime.now()) and 'ongoing' or 'failed'

    @api.depends('deadline_datetime', 'reached_datetime')
    def _compute_exceeded_time(self):
        for r in self:
            r.exceeded_days = 0
            if r.reached_datetime and r.deadline_datetime and r.ticket_id.team_id.resource_calendar_id \
                    and r.reached_datetime > r.deadline_datetime:
                duration = r.ticket_id.team_id.resource_calendar_id.get_work_duration_data(r.deadline_datetime,
                                                                                           r.reached_datetime,
                                                                                           compute_leaves=True)
                r.exceeded_days = duration['days']
