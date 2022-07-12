from odoo import fields, models, api
from odoo.tools.safe_eval import safe_eval


class SaleSubscriptionAutomation(models.Model):
    _name = 'sale.subscription.automation'
    _description = 'Subscription Automated Action'

    @api.model
    def default_get(self, default_fields):
        res = super(SaleSubscriptionAutomation, self).default_get(default_fields)
        res['model_id'] = self.env['ir.model'].search([('model', '=', 'sale.subscription')]).id
        return res

    automation_id = fields.Many2one('base.automation', string='Automated Action', delegate=True, required=True, ondelete='restrict')
    action_to_do = fields.Selection([('next_activity', 'Create a Next Activity'),
                              ('set_tag', 'Update a Analytic Tag'),
                              ('set_stage', 'Update the subscription to a stage'),
                              ('set_to_renew', 'Mark as To Renew'),
                              ('email', 'Send Email')],
                              string='Automated Action To Do', required=True, default='next_activity')
    trigger_on = fields.Selection([('on_create', 'On Creation'),
                                   ('on_write', 'On Update'),
                                   ('on_create_or_write', 'On Creation & Update'),
                                   ('on_unlink', 'On Deletion'),
                                   ('on_time', 'Based on Timed Condition')],
                               string='Trigger Based on', required=True, default='on_create_or_write')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    subscription_template_ids = fields.Many2many('sale.subscription.template', string='On Specific Subscription Templates')
    customer_ids = fields.Many2many('res.partner', string='On Specific Customers')
    company_id = fields.Many2one('res.company', string='Company')
    mrr_min = fields.Monetary('MRR Range Min', currency_field='currency_id')
    mrr_max = fields.Monetary('MRR Range Max', currency_field='currency_id')
    product_ids = fields.Many2many('product.product', string='On Specific Subscription Products', domain=[('product_tmpl_id.subscription_template_id', '!=', False)])
    rating_percentage_satisfaction = fields.Integer('% Happy')
    rating_operator = fields.Selection([('>', 'greater than'),
                                        ('<', 'less than'),
                                        ('>=', 'greater than or equal to'),
                                        ('<=', 'less than or equal to')],
                                        string='Rating Operator', default='>')
    analytic_tag_id = fields.Many2one('account.analytic.tag', string='Analytic Tag')
    stage_id = fields.Many2one('sale.subscription.stage', string='Stage')
    activity_user = fields.Selection([
        ('contract', 'Responsible of Contract'),
        ('channel_leader', 'Sales Channel Leader'),
        ('users', 'Specific Users'),
    ], string='Assign To')
    activity_user_ids = fields.Many2many('res.users', string='Specific Users')
    subscription_count = fields.Integer(compute='_compute_subscription_count', string='Subscription Count')
    date_start = fields.Date(string='Start Date')

    def _compute_subscription_count(self):
        Subscription = self.env['sale.subscription']
        for r in self:
            domain = safe_eval(r.filter_domain) if r.filter_domain else []
            r.subscription_count = Subscription.search_count(domain)

    @api.model
    def create(self, vals):
        vals = self._mapped_fields(vals)
        subscriptions = super(SaleSubscriptionAutomation, self).create(vals)
        subscriptions._update_domain()
        subscriptions._update_automated_action(vals)
        return subscriptions

    def write(self, vals):
        vals = self._mapped_fields(vals)
        res = super(SaleSubscriptionAutomation, self).write(vals)
        self._update_domain()
        self._update_automated_action(vals)
        return res

    @api.model
    def _mapped_fields(self, vals):
        if 'trigger' not in vals and 'trigger_on' in vals:
            vals['trigger'] = vals['trigger_on']
        if 'state' not in vals and 'action_to_do' in vals:
            state = vals['action_to_do']
            if vals['action_to_do'] in ('set_tag', 'set_stage', 'set_to_renew'):
                state = 'object_write'
            vals['state'] = state
        return vals

    def _update_domain(self):
        """
        Updagte filter_pre_domain and filter_domain after create or write a automated action
        """
        for r in self:
            filter_pre_domain = r._prepare_filter_pre_domain()
            filter_domain = r._prepare_filter_domain()
            super(SaleSubscriptionAutomation, r).write({
                'filter_pre_domain': filter_pre_domain,
                'filter_domain': filter_domain,
            })

    def _update_automated_action(self, vals):
        """
        Update action for subscription automated action
        """
        self.filtered(lambda r: r.action_to_do != 'next_activity' and r.child_ids).unlink()
        for r in self:
            if r.action_to_do in ('next_activity', 'email'):
                super(SaleSubscriptionAutomation, r).write({'action_to_do': r.action_to_do})
            elif r.action_to_do == 'set_tag' and r.analytic_tag_id:
                r._update_fields_lines_to_write('analytic_tag_ids', r.analytic_tag_id.id)
            elif r.action_to_do == 'set_stage' and r.stage_id:
                r._update_fields_lines_to_write('stage_id', r.stage_id.id)
            elif r.action_to_do == 'set_to_renew':
                r._update_fields_lines_to_write('to_renew', True)

    def _prepare_filter_pre_domain(self):
        """
        Hook method to prepare filter_pre_domain
        """
        self.ensure_one()
        domain = []
        if self.date_start:
            domain += [('date_start', '>=', self.date_start)]
        return domain

    def _prepare_filter_domain(self):
        """
        Hook method to prepare filter domain
        """
        self.ensure_one()
        domain = []
        if self.subscription_template_ids:
            domain += [('template_id', 'in', self.subscription_template_ids.ids)]
        if self.customer_ids:
            domain += [('partner_id', 'in', self.customer_ids.ids)]
        if self.company_id:
            domain += [('company_id', '=', self.company_id.id)]
        if self.mrr_min:
            domain += [('recurring_monthly', '>=', self.mrr_min)]
        if self.mrr_max:
            domain += [('recurring_monthly', '<=', self.mrr_max)]
        if self.product_ids:
            domain += [('template_id', 'in', self.product_ids.mapped('product_tmpl_id.subscription_template_id').ids)]
        if self.rating_percentage_satisfaction:
            domain += [('rating_percentage_satisfaction', self.rating_operator, self.rating_percentage_satisfaction)]
        if self.date_start:
            domain += [('date_start', '>=', self.date_start)]
        return domain

    def _prepare_fields_lines_val(self, field, value):
        """
        Hook method to prepare file value
        """
        res = {
            'state': 'object_write',
            'fields_lines': [(5, 0, 0), (0, False, {
                'col1': field.id,
                'value': value})
            ]}
        return res

    def _update_fields_lines_to_write(self, field_name, value):
        """
        Update fields lines to write from automated action
        """
        self.ensure_one()
        field = self.env['ir.model.fields'].search([('model', '=', self.model_name), ('name', '=', field_name)], limit=1)
        vals = self._prepare_fields_lines_val(field, value)
        super(SaleSubscriptionAutomation, self).write(vals)

    def action_view_subscriptions(self):
        self.ensure_one()
        domain = []
        if self.filter_domain:
            domain += safe_eval(self.filter_domain)
        if self.subscription_template_ids:
            domain += [('template_id', 'in', self.subscription_template_ids.ids)]
        action = self.env['ir.actions.act_window']._for_xml_id('to_sale_subscription.sale_subscription_action')

        context = dict(action.get('context', {}))
        if len(self.subscription_template_ids) == 1:
            context['default_template_id'] = self.subscription_template_ids[0].id

        action['domain'] = domain
        action['context'] = context
        return action
