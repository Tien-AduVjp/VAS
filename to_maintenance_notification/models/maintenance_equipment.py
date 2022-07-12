# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields, models, api, _

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    days_to_notify = fields.Integer(string='Days to Notify', related='category_id.days_to_notify', store=True)
    
    next_maintenance_milestone_id = fields.Many2one('product.milestone', string='Next Maintenance Milestone', compute= '_compute_next_maintenance', store=True)


    @api.model
    def _get_next_action_date_by_working_frequency(self):
        
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
            milestone_ids = self.maintenance_schedule_ids.product_milestone_id.filtered(lambda l: l.operation_time == True or l.uom_id.category_id.measure_type != 'working_time')
            milestone_ids = milestone_ids -  done_milestone_ids
            if milestone_ids:
                for working_frequency in self.equipment_working_frequency_ids:
                    for milestone in milestone_ids:
                        days = working_frequency._get_milestone_maintenance_days(milestone)
                        if days and (next_days == 0 or days < next_days):
                            next_days = days
                            next_milestone = milestone

            real_time_milestone_ids = self.maintenance_schedule_ids.product_milestone_id.filtered(lambda l: l.operation_time != True and l.uom_id.category_id.measure_type == 'working_time') 
            if real_time_milestone_ids and self.effective_date:
                total_working_time = date_now - self.effective_date
                day_uom = self.env.ref('uom.product_uom_day')
                nearest_milestone = None
                nearest_time = 0
                for milestone in real_time_milestone_ids:
                    gap = milestone.uom_id._compute_quantity(milestone.amount, day_uom) - total_working_time.days
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
                return (date_now + timedelta(days=next_days)), next_milestone
            return None, None

    @api.depends('period', 'maintenance_ids.request_date', 'maintenance_ids.close_date', 'effective_date',
                 'maintenance_schedule_ids', 'equipment_working_frequency_ids')
    def _compute_next_maintenance(self):
        super(MaintenanceEquipment, self)._compute_next_maintenance()

        for r in self.filtered(lambda r: r.maintenance_schedule_ids):
            next_date, next_milestone = r._get_next_action_date_by_working_frequency()
            if next_date:
                r.next_action_date = next_date
                r.next_maintenance_milestone_id = next_milestone and next_milestone.id or False
            else:
                r.next_maintenance_milestone_id = False

    def _create_new_request(self, date):
        # TODO: call super method instead
        maintenance_team_id = self.maintenance_team_id or self.env.ref('maintenance.equipment_team_maintenance')
        maintenance_milestone_id = self.next_maintenance_milestone_id.id if self.maintenance_schedule_ids else False
        self.ensure_one()
        self.env['maintenance.request'].create({
            'name': _('Preventive Maintenance - %s') % self.name,
            'request_date': date,
            'schedule_date': date,
            'maintenance_milestone_id': maintenance_milestone_id,
            'category_id': self.category_id.id,
            'equipment_id': self.id,
            'maintenance_type': 'preventive',
            'owner_user_id': self.owner_user_id.id,
            'user_id': self.technician_user_id.id,
            'maintenance_team_id': maintenance_team_id.id,
            'duration': self.maintenance_duration,
            'company_id': self.company_id.id
            })

    @api.model
    def _cron_generate_requests(self):
        #TODO: R&D to merge with to_maintenance_by_working_hours in ver 14.0
        super(MaintenanceEquipment, self)._cron_generate_requests()

        for equipment in self.search([('maintenance_schedule_ids', '!=', False)]):
            equipment._compute_next_maintenance()
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
            
