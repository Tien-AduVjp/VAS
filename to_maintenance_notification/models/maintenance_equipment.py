from datetime import timedelta, datetime, time

from odoo import fields, models, api


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    days_to_notify = fields.Integer(string='Days to Notify', related='category_id.days_to_notify', store=True)
    next_maintenance_milestone_id = fields.Many2one('product.milestone', string='Next Maintenance Milestone', compute= '_compute_next_maintenance', store=True)
    preventive_maintenance_mode = fields.Selection(selection_add=[('schedule', 'By Schedule')], ondelete={'schedule': 'set default'})

    def _get_total_working_day(self, total_time):
        self.ensure_one()
        dt = datetime.combine(self.effective_date, time.min)
        resource_calendar = (self.resource_calendar_id
                             or self.company_id.resource_calendar_id
                             or self.env.company.resource_calendar_id)
        return (resource_calendar.plan_hours(total_time, dt).date() - self.effective_date).days

    def _get_next_action_date_by_working_frequency(self):
        self.ensure_one()
        MaintenanceRequest = self.env['maintenance.request']
        date_now = fields.Date.context_today(self)
        open_maintenance_todo = MaintenanceRequest.search([
            ('equipment_id', '=', self.id),
            ('maintenance_type', '=', 'preventive'),
            ('company_id', '=', self.company_id.id),
            ('stage_id.done', '!=', True),
            ('close_date', '=', False)], order="request_date asc", limit=1)
        #do not create new request if this equipment has opening maintenance request
        if open_maintenance_todo:
            return open_maintenance_todo.request_date, None
        else:
            next_days = 0
            next_milestone = None
            #get nearest maintenance milestone based on maintenance schedule and working frequency
            done_milestone_ids = self.maintenance_ids.filtered(lambda l: l.maintenance_type == 'preventive' and l.stage_id.done == True).mapped('maintenance_milestone_id')
            milestone_ids = self.maintenance_schedule_ids.mapped('product_milestone_id').filtered(lambda l: l.uom_id.category_id != self.env.ref('uom.uom_categ_wtime'))
            milestone_ids = milestone_ids - done_milestone_ids
            if milestone_ids:
                for working_frequency in self.equipment_working_frequency_ids:
                    for milestone in milestone_ids:
                        days = working_frequency._get_milestone_maintenance_days(milestone)
                        if days and (next_days == 0 or days < next_days):
                            next_days = days
                            next_milestone = milestone

            real_time_milestone_ids = self.maintenance_schedule_ids.mapped('product_milestone_id').filtered(lambda l: l.uom_id.category_id == self.env.ref('uom.uom_categ_wtime'))
            if real_time_milestone_ids and self.effective_date:
                total_working_day = 0
                day_uom = self.env.ref('uom.product_uom_day')
                time_uom = self.env.ref('uom.product_uom_hour')
                nearest_milestone = None
                nearest_time = 0
                for milestone in real_time_milestone_ids - done_milestone_ids:
                    if milestone.uom_id == day_uom:
                        total_working_day = milestone.amount
                    else:
                        total_time = milestone.uom_id._compute_quantity(milestone.amount, time_uom)
                        total_working_day = self._get_total_working_day(total_time) if total_time else 0
                    gap = total_working_day
                    if gap > 0 and (nearest_time == 0 or nearest_time > gap):
                        nearest_time = gap
                        nearest_milestone = milestone
                if next_days and next_milestone:
                    if nearest_time and nearest_time < next_days:
                        next_days = nearest_time
                        next_milestone = nearest_milestone
                else:
                    next_days = nearest_time
                    next_milestone = nearest_milestone
            if next_days and next_milestone:
                next_date = self.effective_date + timedelta(days=next_days)
                return next_date if next_date > date_now else date_now, next_milestone
            return None, None

    @api.onchange('preventive_maintenance_mode')
    def _onchange_period_with_schedule(self):
        if self.preventive_maintenance_mode == 'schedule':
            self.period = self._calculate_period_with_schedule()

    def _calculate_period_with_schedule(self):
        self.ensure_one()
        return 0

    @api.depends('maintenance_schedule_ids', 'equipment_working_frequency_ids')
    def _compute_next_maintenance(self):
        scheduled_maintenance_equipments = self.filtered(lambda e: e.maintenance_schedule_ids and e.preventive_maintenance_mode == 'schedule')
        for equipment in scheduled_maintenance_equipments:
            next_date, next_milestone = equipment._get_next_action_date_by_working_frequency()
            if next_date:
                equipment.next_action_date = next_date
                equipment.next_maintenance_milestone_id = next_milestone
            else:
                equipment.next_action_date = False
                equipment.next_maintenance_milestone_id = False
        (self - scheduled_maintenance_equipments).next_maintenance_milestone_id = False
        return super(MaintenanceEquipment, self - scheduled_maintenance_equipments)._compute_next_maintenance()

    def _prepare_maintenance_request_vals(self, date):
        res = super(MaintenanceEquipment, self)._prepare_maintenance_request_vals(date)
        maintenance_team_id = self.maintenance_team_id or self.env.ref('maintenance.equipment_team_maintenance')
        maintenance_milestone_id = self.next_maintenance_milestone_id.id if self.maintenance_schedule_ids else False
        res.update({
            'maintenance_team_id': maintenance_team_id.id,
            'maintenance_milestone_id': maintenance_milestone_id,
        })
        return res

    @api.model
    def _cron_generate_requests(self):
        for equipment in self.search([('maintenance_schedule_ids', '!=', False), ('preventive_maintenance_mode', '=', 'schedule')]):
            next_requests = self.env['maintenance.request'].search([('stage_id.done', '=', False),
                                                    ('equipment_id', '=', equipment.id),
                                                    ('company_id', '=', equipment.company_id.id),
                                                    ('maintenance_type', '=', 'preventive'),
                                                    ('request_date', '=', equipment.next_action_date)], limit = 1)
            if equipment.next_maintenance_milestone_id:
                if not next_requests:
                    equipment._create_new_request(equipment.next_action_date)
                else:
                    next_requests.write({'maintenance_milestone_id': equipment.next_maintenance_milestone_id.id})
        return super(MaintenanceEquipment, self)._cron_generate_requests()
