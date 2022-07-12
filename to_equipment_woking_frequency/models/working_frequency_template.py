from odoo import models, fields, api, _


class WorkingFrequencyTemplate(models.Model):
    _name = 'working.frequency.template'
    _description = 'Working Frequency Template'

    @api.model
    def _get_working_uom_id_domain(self):
        return [('category_id.id', '!=', self.env.ref('uom.uom_categ_wtime').id)]

    working_amount = fields.Float(string='Working Amount', required=True)
    working_uom_id = fields.Many2one('uom.uom', string='Working Amount UoM', required=True, domain=_get_working_uom_id_domain)
    period_time = fields.Float(string='Period Time (Hours)', required=True)

    _sql_constraints = [
        ('working_frequency_unique',
         'unique(working_amount, working_uom_id, period_time)',
         _("Working frequency must be unique!")),

        ('working_amount_check',
         'CHECK(working_amount >= 0)',
         "Working Amount must be greater than or equal to zero!"),

         ('period_time_check',
         'CHECK(period_time >= 0)',
         "Period Time must be greater than or equal to zero!"),
    ]

    def _prepare_equipment_working_frequency_data(self):
        return {
            'working_amount': self.working_amount,
            'working_uom_id': self.working_uom_id.id,
            'period_time': self.period_time,
            }

    def name_get(self):
        return [(p.id, "%s %s per %s hours" % (p.working_amount, p.working_uom_id.name, p.period_time)) for p in self]
