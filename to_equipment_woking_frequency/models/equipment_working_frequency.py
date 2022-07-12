from odoo import models, fields, api, _


class EquipmentWorkingFrequency(models.Model):
    _name = 'equipment.working.frequency'
    _description = 'Equipment Working Frequency'

    @api.model
    def _get_period_time_uom_id_domain(self):
        return [('category_id.id', '=', self.env.ref('uom.uom_categ_wtime').id)]

    equipment_id = fields.Many2one('maintenance.equipment')
    start_amount = fields.Float('Starting Amount', default=0.0, required=True)
    working_amount = fields.Float('Working Amount', required=True)
    working_uom_id = fields.Many2one('uom.uom', string='Working Amount UoM', required=True)
    period_time = fields.Float('Period Time', required=True)
    period_time_uom_id = fields.Many2one('uom.uom', string='Period Time UoM', required=True, domain=_get_period_time_uom_id_domain)
    total_working_amount = fields.Float('Total Working', compute='_compute_total_working_amount', inverse='_set_total_working_amount', store=True)

    _sql_constraints = [
        ('working_frequency_unique',
         'unique(equipment_id,working_uom_id)',
         _("Working frequency must be unique!")),

         ('working_amount_check',
         'CHECK(working_amount >= 0)',
         "Working Amount must be greater than or equal to zero!"),

         ('period_time_check',
         'CHECK(period_time >= 0)',
         "Period Time must be greater than or equal to zero!"),

         ('total_working_amount_check',
         'CHECK(total_working_amount >= 0)',
         "Total Working Amount must be greater than or equal to zero!"),

         ('start_amount_check',
         'CHECK(start_amount >= 0)',
         "Starting Amount must be greater than or equal to zero!")
    ]

    @api.depends('working_amount', 'period_time', 'start_amount', 'period_time_uom_id')
    def _compute_total_working_amount(self):
        day_uom = self.env.ref('uom.product_uom_day')
        date_now = fields.Date.context_today(self)
        for r in self:
            total_working_amount = 0.0
            if r.equipment_id.effective_date and r.working_amount and r.period_time and r.period_time_uom_id:
                day_amount = r.working_amount / r.period_time_uom_id._compute_quantity(r.period_time, day_uom)
                delta = date_now - r.equipment_id.effective_date
                if delta.days < 0 :
                    total_working_amount = r.start_amount
                else:
                    total_working_amount = r.start_amount + day_amount * delta.days
            r.total_working_amount = total_working_amount

    def _set_total_working_amount(self):
        day_uom = self.env.ref('uom.product_uom_day')
        date_now = fields.Date.context_today(self)
        for r in self:        
            working_amount = r.working_amount or 0.0
            if r.equipment_id.effective_date and r.period_time and r.period_time_uom_id and r.working_uom_id:
                delta = date_now - r.equipment_id.effective_date
                if delta.days > 0 and r.total_working_amount > r.start_amount:
                    day_amount = (r.total_working_amount - r.start_amount) / delta.days                  
                    working_amount = r.period_time_uom_id._compute_quantity(r.period_time, day_uom) * day_amount
            r.working_amount = working_amount

    def name_get(self):
        return [(p.id, "%s %s(s) per %s %s(s)" % (p.working_amount, p.working_uom_id.name, p.period_time, p.period_time_uom_id.name)) for p in self]
