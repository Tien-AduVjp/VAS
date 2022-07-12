from datetime import timedelta

from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from odoo.exceptions import ValidationError


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    ave_daily_working_hours = fields.Float(string='Ave. Daily Working Hours', default=0.0,
                                           help="The average daily working hours of the equipment")

    working_hour_period = fields.Float(string='Working Hours between each preventive maintenance', default=0.0,
                                       help="The working hours of the equipment between each preventive maintenance")

    _sql_constraints = [
        ('ave_daily_working_hoursn_check',
         'CHECK(ave_daily_working_hours >= 0)',
         "Ave. Daily Working Hours must be greater than or equal to zero!"),

         ('working_hour_period_check',
         'CHECK(working_hour_period >= 0)',
         "Working Hours between each preventive maintenance must be greater than or equal to zero!"),
    ]
    
    @api.constrains('period', 'working_hour_period')
    def _check_maintenance_team_id(self):
        for r in self:
            if (r.period != 0 or r.working_hour_period != 0) and not r.maintenance_team_id:
                raise ValidationError(_("Select an Maintenance Team on equipment '%s', please") % r.name)

    @api.model
    def _get_next_action_date_by_working_hours(self):
        MaintenanceRequest = self.env['maintenance.request']
        if not float_is_zero(self.ave_daily_working_hours, precision_digits=2):
            working_day_period = self.working_hour_period / self.ave_daily_working_hours
        else:
            working_day_period = 0.0

        date_now = fields.Date.context_today(self)
        next_maintenance_todo = MaintenanceRequest.search([
            ('equipment_id', '=', self.id),
            ('maintenance_type', '=', 'preventive'),
            ('stage_id.done', '!=', True),
            ('close_date', '=', False)], order="request_date asc", limit=1)
        last_maintenance_done = MaintenanceRequest.search([
            ('equipment_id', '=', self.id),
            ('maintenance_type', '=', 'preventive'),
            ('stage_id.done', '=', True),
            ('close_date', '!=', False)], order="close_date desc", limit=1)
        if next_maintenance_todo and last_maintenance_done:
            next_date = next_maintenance_todo.request_date
            date_gap = fields.Date.from_string(next_maintenance_todo.request_date) - fields.Date.from_string(last_maintenance_done.close_date)
            # If the gap between the last_maintenance_done and the next_maintenance_todo one is bigger than 2 times the working_day_period and next request is in the future
            # We use 2 times the working_day_period to avoid creation too closed request from a manually one created
            if date_gap > timedelta(0) and date_gap > timedelta(days=working_day_period) * 2 and fields.Date.from_string(next_maintenance_todo.request_date) > fields.Date.from_string(date_now):
                # If the new date still in the past, we set it for today
                if fields.Date.from_string(last_maintenance_done.close_date) + timedelta(days=working_day_period) < fields.Date.from_string(date_now):
                    next_date = date_now
                else:
                    next_date = fields.Date.to_string(fields.Date.from_string(last_maintenance_done.close_date) + timedelta(days=working_day_period))
        elif next_maintenance_todo:
            next_date = next_maintenance_todo.request_date
            date_gap = fields.Date.from_string(next_maintenance_todo.request_date) - fields.Date.from_string(date_now)
            # If next maintenance to do is in the future, and in more than 2 times the working_day_period, we insert an new request
            # We use 2 times the working_day_period to avoid creation too closed request from a manually one created
            if date_gap > timedelta(0) and date_gap > timedelta(days=working_day_period) * 2:
                next_date = fields.Date.to_string(fields.Date.from_string(date_now) + timedelta(days=working_day_period))
        elif last_maintenance_done:
            next_date = fields.Date.from_string(last_maintenance_done.close_date) + timedelta(days=working_day_period)
            # If when we add the working_day_period to the last maintenance done and we still in past, we plan it for today
            if next_date < fields.Date.from_string(date_now):
                next_date = date_now
            else:
                next_date = fields.Date.to_string(next_date)
        else:
            next_date = fields.Date.to_string(fields.Date.from_string(date_now) + timedelta(days=working_day_period))

        return next_date

    @api.depends('period', 'working_hour_period', 'ave_daily_working_hours', 'maintenance_ids.request_date', 'maintenance_ids.close_date')
    def _compute_next_maintenance(self):
        super(MaintenanceEquipment, self)._compute_next_maintenance()

        for equipment in self.filtered(lambda x: x.working_hour_period > 0):
            next_date = equipment._get_next_action_date_by_working_hours()

            if equipment.next_action_date:
                if fields.Date.from_string(next_date) < fields.Date.from_string(equipment.next_action_date):
                    equipment.next_action_date = next_date
            else:
                equipment.next_action_date = next_date

    @api.model
    def _cron_generate_requests(self):
        """
            Generates maintenance request on the next_action_date or today if none exists
        """
        #TODO: R&D to merge with to_maintenance_notification in ver 14.0
        for equipment in self.search([('working_hour_period', '>', 0)]):
            next_requests = self.env['maintenance.request'].search([('stage_id.done', '=', False),
                                                    ('equipment_id', '=', equipment.id),
                                                    ('maintenance_type', '=', 'preventive'),
                                                    ('request_date', '=', equipment.next_action_date)])
            if not next_requests:
                equipment._create_new_request(equipment.next_action_date)
                

        return super(MaintenanceEquipment, self)._cron_generate_requests()
