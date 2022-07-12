from odoo import fields, models, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import timedelta


class AbstractFleetInsurance(models.AbstractModel):
    _name = 'abstract.fleet.insurance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_end, date_start'
    _description = 'Share business Logics between Fleet Insurance models'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired')], string='Status', default='draft', required=True, readonly=True, tracking=True)

    name = fields.Char(string='Reference', required=True, readonly=False, states={'confirmed': [('readonly', True)],
                                                                                  'cancelled': [('readonly', True)],
                                                                                  'expired': [('readonly', True)]}, tracking=True,)

    fleet_insurance_type_id = fields.Many2one('fleet.insurance.type', string='Type', required=True, ondelete='restrict',
                                              readonly=False, states={'confirmed': [('readonly', True)],
                                                                      'cancelled': [('readonly', True)],
                                                                      'expired': [('readonly', True)]},
                                              tracking=True)

    date_start = fields.Date(string='Start Date', required=True, default=fields.Date.today,
                             tracking=True,
                             readonly=False, states={'confirmed': [('readonly', True)],
                                                     'cancelled': [('readonly', True)],
                                                     'expired': [('readonly', True)]},
                             help="The date on which the insurance starts")

    date_end = fields.Date(string='Expiry', required=True, readonly=False, states={'confirmed': [('readonly', True)],
                                                                                   'cancelled': [('readonly', True)],
                                                                                   'expired': [('readonly', True)]},
                           tracking=True, compute='_compute_date_end', store=True, copy=True,
                           help="The date on which the insurance gets expired")

    days_to_notify = fields.Integer(string='Days to Notify', default=7, tracking=True, required=True, compute='_compute_days_to_notify',
                                    store=True, readonly=False,
                                    help="The number of days prior to the expiry date on which a"
                                         " notification will be posted to the followers of this documents. Input zero to disable notification.")

    _sql_constraints = [
        ('positive_days_to_notify_check',
         'CHECK(days_to_notify >= 0)',
         "Days to Notify must be greater than or equal to zero!"),
    ]

    @api.depends('fleet_insurance_type_id', 'fleet_insurance_type_id.period', 'date_start')
    def _compute_date_end(self):
        for r in self:
            date_end = False
            if r.fleet_insurance_type_id and r.fleet_insurance_type_id.period > 0 and r.date_start:
                date_end = fields.Date.from_string(r.date_start) + relativedelta(months=r.fleet_insurance_type_id.period)
            r.date_end = date_end

    @api.depends('fleet_insurance_type_id', 'fleet_insurance_type_id.days_to_notify')
    def _compute_days_to_notify(self):
        for r in self:
            days_to_notify = 0
            if r.fleet_insurance_type_id and r.fleet_insurance_type_id.days_to_notify > 0:
                days_to_notify = r.fleet_insurance_type_id.days_to_notify
            r.days_to_notify = days_to_notify

    def action_confirm(self):
        self.write({'state':'confirmed'})

    def action_cancel(self):
        self.write({'state':'cancelled'})

    def action_set_expire(self):
        values= {'state': 'expired'}
        today = fields.Date.today()
        if self.date_end > today:
            values.update({'date_end': today})
        self.write(values)

    def action_set_draft(self):

        self.write({'state':'draft'})

    def unlink(self):
        if any(r.state != 'draft' for r in self):
            raise UserError(_("You cannot delete an insurance that is not in draft state!"))
        return super(AbstractFleetInsurance, self).unlink()

    def action_cron_set_expired(self):
        today = fields.Date.today()
        insurances = self.search([('state', '=', 'confirmed'), ('date_end', '<=', today)])
        if insurances:
            insurances.action_set_expire()

    def action_cron_send_expire_notice(self):
        today = fields.Date.from_string(fields.Date.today())

        confirmed_insurances = self.search([('state', '=', 'confirmed'), ('days_to_notify', '>', 0)])

        for insurance in confirmed_insurances:
            date_end = fields.Date.from_string(insurance.date_end)
            date_to_notify = date_end - timedelta(days=insurance.days_to_notify)
            if date_to_notify <= today:
                insurance.expiry_warning()
