from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FleetDriverLicense(models.Model):
    _name = 'fleet.driver.license'
    _description = 'Driver License'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'legal_number'

    legal_number = fields.Char(string='Legal Number', required=True, size=20, readonly=False,
                               states={
                                   'confirmed': [('readonly', True)],
                                   'expired': [('readonly', True)]
                                   }, tracking=True)
    driver_id = fields.Many2one('res.partner', 'Driver', required=True, readonly=False,
                                states={
                                    'confirmed': [('readonly', True)],
                                    'expired': [('readonly', True)]
                                    }, tracking=True, help="The driver who holds this license")

    class_id = fields.Many2one('driver.license.class', string='Class', help='The class of this license.', readonly=False,
                                states={'confirmed': [('readonly', True)],
                                        'expired': [('readonly', True)]}, tracking=True)
    issued_date = fields.Date(string='Date Issued', help="The date on which this license was issued", readonly=False,
                                states={'confirmed': [('readonly', True)],
                                        'expired': [('readonly', True)]}, tracking=True)
    expired_date = fields.Date(string='Expiry', help="The date on which this license to be expired. Leave it blank for non-expiration", readonly=False,
                                states={'confirmed': [('readonly', True)],
                                        'expired': [('readonly', True)]}, tracking=True)

    issued_by = fields.Many2one('res.partner', string='Issued by', help="The authority that issued this license",
                                domain=[('is_company', '=', True)], readonly=False,
                                states={
                                    'confirmed': [('readonly', True)],
                                    'expired': [('readonly', True)]
                                    }, tracking=True)

    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('expired', 'Expired')
                              ], required=True, default='draft', index=True, readonly=True, string='Status', tracking=True, copy=False)

    days_left = fields.Integer(string='Days to Expiry', compute='_compute_days_left', help="The number of days to the expired date")

    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, legal_number=_("%s (copy)") % (self.legal_number))
        return super(FleetDriverLicense, self).copy(default=default)

    @api.depends('expired_date')
    def _compute_days_left(self):
        for r in self:
            if not r.expired_date:
                r.days_left = 100000  # force to ab't 300 years ^_^
            else:
                now_date = fields.Date.today()
                r.days_left = (r.expired_date - now_date).days

    @api.constrains('legal_number')
    def _check_legal_number(self):
        for r in self:
            overlap = self.env['fleet.driver.license'].search([
                ('id', '!=', r.id),
                ('legal_number', '=', r.legal_number)
                ], limit=1)
            if overlap:
                raise UserError(_("There was a license of the same Legal Number '%s' that already exists.") % overlap.display_name)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_set_expired(self):
        license_unqualified = self.filtered(lambda r: r.state != 'confirmed')
        if not self._context.get('cron_mode', False) and license_unqualified:
            raise UserError(_("Only licenses in confirmed state can be set to expired: %s") % ','.join(license_unqualified.mapped('legal_number')))
        (self - license_unqualified).write({'state': 'expired'})

    def unlink(self):
        for r in self:
            if r.state != 'draft':
                raise UserError(_("You can only delete licenses which are in draft state!"))
        return super(FleetDriverLicense, self).unlink()

    def cron_find_and_set_expire(self):
        to_set_exprire = self.search([('state', '=', 'confirmed'), ('expired_date', '<=', fields.Date.today())])
        if to_set_exprire:
            to_set_exprire.with_context(cron_mode=True).action_set_expired()
        return True

