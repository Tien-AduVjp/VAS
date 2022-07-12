from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class SaleSubscriptionTemplate(models.Model):
    _name = 'sale.subscription.template'
    _description = 'Sale Subscription Template'
    _inherit = 'mail.thread'

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    code = fields.Char()
    description = fields.Text(translate=True, string='Terms and Conditions')
    recurring_rule_type = fields.Selection([('daily', 'Day(s)'), ('weekly', 'Week(s)'),
                                            ('monthly', 'Month(s)'), ('yearly', 'Year(s)'), ],
                                           string='Recurrence', required=True,
                                           help="Invoice will repeat based on recurring interval.",
                                           default='monthly', track_visibility='onchange')
    recurring_interval = fields.Integer(string='Repeat Every', help="Repeat per (Days/Week/Month/Year)", required=True, default=1, track_visibility='onchange')

    payment_mode = fields.Selection([
        ('manual', 'Manual'),
        ('draft_invoice', 'Draft invoice'),
        ('validate_send', 'Invoice'),
        ('validate_send_payment', 'Invoice & try to charge'),
        ('success_payment', 'Invoice only on successful payment'),
    ], required=True, default='draft_invoice')
    product_ids = fields.One2many('product.template', 'subscription_template_id', copy=True)
    journal_id = fields.Many2one('account.journal', string='Accounting Journal', domain="[('type', '=', 'sale')]", company_dependent=True,
                                 help="Subscriptions will use this journal to generate invoice; "
                                      "otherwise the sales journal with the lowest order is used.")
    analytic_tag_ids = fields.Many2many('account.analytic.tag', 'sale_subscription_template_tag_rel', 'template_id', 'analytic_tag_id', string='Analytic Tags')
    product_count = fields.Integer(compute='_compute_product_count')
    subscription_count = fields.Integer(compute='_compute_subscription_count')
    color = fields.Integer()
    closed_automatically_after = fields.Integer(string='Subscription closed automatically after', default=30,
                                      help="The number of days before subscriptions are closed automatically when system cannot payment automatically after multiple attempts.")
    invoice_mail_template_id = fields.Many2one('mail.template', string='Invoice Email Template', domain=[('model', '=', 'account.invoice')])

    @api.constrains('recurring_interval')
    def _check_recurring_interval(self):
        for r in self:
            if r.recurring_interval <= 0:
                raise ValidationError(_("The recurring interval of Subscription template %s must be positive") % r.name)

    def _compute_subscription_count(self):
        subscription_data = self.env['sale.subscription'].read_group([('template_id', 'in', self.ids), ('stage_id', '!=', False)],
                                                                     ['template_id'],
                                                                     ['template_id'])
        mapped_data = dict([(s['template_id'][0], s['template_id_count']) for s in subscription_data])
        for r in self:
            r.subscription_count = mapped_data.get(r.id, 0)

    def _compute_product_count(self):
        product_data = self.env['product.template'].sudo().read_group([('subscription_template_id', 'in', self.ids)],
                                                                      ['subscription_template_id'],
                                                                      ['subscription_template_id'])
        mapped_data = dict((data['subscription_template_id'][0], data['subscription_template_id_count']) for data in product_data)
        for r in self:
            r.product_count = mapped_data.get(r.id, 0)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            connector = '&' if operator in expression.NEGATIVE_TERM_OPERATORS else '|'
            domain = [connector, ('code', operator, name), ('name', operator, name)]
        subscription_template_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return self.browse(subscription_template_ids).name_get()

    def name_get(self):
        res = []
        for r in self:
            name = r.name
            if r.code:
                name = '%s - %s' % (r.code, r.name)
            res.append((r.id, name))
        return res

