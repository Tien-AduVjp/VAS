import datetime
import logging
import traceback

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from uuid import uuid4

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import float_is_zero, format_date
from odoo.tools.safe_eval import safe_eval

from .sale_order_line import PERIODS

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _name = 'sale.subscription'
    _description = 'Sale Subscription'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'rating.mixin']

    def _get_default_stage_id(self):
        return self.env['sale.subscription.stage'].search([], order='sequence', limit=1)

    def _get_default_pricelist(self):
        return self.env['product.pricelist'].search([('currency_id', '=', self.env.company.currency_id.id)], limit=1).id

    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]

    name = fields.Char(required=True, tracking=True, default="New")
    code = fields.Char(string="Reference", required=True, tracking=True, index=True, copy=False)
    stage_id = fields.Many2one(
        'sale.subscription.stage', string='Stage', index=True,
        default=lambda s: s._get_default_stage_id(), group_expand='_read_group_stage_ids', tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, auto_join=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    date_start = fields.Date(string='Start Date', default=fields.Date.today)
    date_end = fields.Date(string='End Date', tracking=True,
        help="Subscription will be closed on this date and it will be pending 1 month before this date.")
    color = fields.Integer('Color Index', default=0)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', default=_get_default_pricelist, required=True)
    currency_id = fields.Many2one('res.currency', related='pricelist_id.currency_id', string='Currency', readonly=True)
    company_currency = fields.Many2one('res.currency', string='Company Currency', related='company_id.currency_id', readonly=True)
    line_ids = fields.One2many('sale.subscription.line', 'subscription_id', string='Invoice Lines', copy=True)
    recurring_rule_type = fields.Selection(string='Recurrence', related="template_id.recurring_rule_type", readonly=1,
        help="Invoice will repeat based on recurring interval.")
    recurring_interval = fields.Integer(string='Repeat Every', related="template_id.recurring_interval", readonly=1,
        help="Repeat per (Days/Week/Month/Year)")
    recurring_next_date = fields.Date(string='Date of Next Invoice', default=fields.Date.today,
        help="The next invoice will be generated on this date and the period will be followed up from this date.")
    recurring_total = fields.Float(compute='_compute_recurring_total', string="Recurring Price", store=True, tracking=True)
    recurring_monthly = fields.Float(compute='_compute_recurring_monthly', string="Monthly Recurring Revenue", store=True)
    close_reason_id = fields.Many2one("sale.subscription.close.reason", string="Close Reason", tracking=True)
    template_id = fields.Many2one('sale.subscription.template', string='Subscription Template', required=True, tracking=True)
    payment_mode = fields.Selection(related='template_id.payment_mode', readonly=False)
    description = fields.Text()
    user_id = fields.Many2one('res.users', string='Salesperson', tracking=True, default=lambda self: self.env.user)
    team_id = fields.Many2one('crm.team', 'Sales Team', change_default=True, default=False)
    team_user_id = fields.Many2one('res.users', string="Team Leader", related="team_id.user_id", readonly=False)
    invoice_count = fields.Integer(compute='_compute_invoice_count')
    country_id = fields.Many2one('res.country', related='partner_id.country_id', store=True, readonly=False)
    industry_id = fields.Many2one('res.partner.industry', related='partner_id.industry_id', store=True, readonly=False)
    sale_order_count = fields.Integer(compute='_compute_sale_order_count')
    # customer portal
    uuid = fields.Char('Account UUID', default=lambda self: str(uuid4()), copy=False, required=True)
    website_url = fields.Char('Website URL', compute='_compute_website_url', help='The full URL to access the document via the website.')
    payment_token_id = fields.Many2one('payment.token', 'Payment Token', domain="[('partner_id','=',partner_id)]",
        help='If set, subscription will use this is payment token. Otherwise, it will use the default payment token of partner.')
    # add tax calculation
    recurring_amount_tax = fields.Float('Taxes', compute="_compute_amount_all")
    recurring_amount_total = fields.Float('Total', compute='_compute_amount_all')
    favorite_user_ids = fields.Many2many(
        'res.users', 'subscription_favorite_user_rel', 'subscription_id', 'user_id',
        default=_get_default_favorite_user_ids,
        string='Members')
    is_favorite = fields.Boolean(compute='_compute_is_favorite', inverse='_inverse_is_favorite', string='Show Subscription on dashboard',
        help="Whether this subscription should be displayed on your dashboard.")
    kpi_1month_mrr_delta = fields.Float('KPI 1 Month MRR Delta')
    kpi_1month_mrr_percentage = fields.Float('KPI 1 Month MRR Percentage')
    kpi_3months_mrr_delta = fields.Float('KPI 3 months MRR Delta')
    kpi_3months_mrr_percentage = fields.Float('KPI 3 Months MRR Percentage')
    rating_percentage_satisfaction = fields.Integer(
        compute='_compute_rating_percentage_satisfaction', string='% Happy', store=True,
        help="The ratio between the 'great' ratings and the total number of ratings")
    in_progress = fields.Boolean(related='stage_id.in_progress')
    to_renew = fields.Boolean(string='To Renew', default=False, copy=False)

    # rating fields
    rating_request_deadline = fields.Datetime(compute='_compute_rating_request_deadline', store=True)
    rating_status = fields.Selection([('stage', 'Rating when changing stage'), ('periodic', 'Periodical Rating'), ('no','No rating')], 'Customer(s) Ratings', help="How to get customer feedback?\n"
                    "- Rating when changing stage: an email will be sent when a subscription is pulled in another stage.\n"
                    "- Periodical Rating: email will be sent periodically.\n\n"
                    "Don't forget to set up the mail templates on the stages for which you want to get the customer's feedbacks.", default="no", required=True)
    rating_status_period = fields.Selection([
        ('daily', 'Daily'), ('weekly', 'Weekly'), ('bimonthly', 'Twice a Month'),
        ('monthly', 'Once a Month'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')
    ], 'Rating Frequency')

    portal_show_rating = fields.Boolean('Rating visible publicly', copy=False)

    _sql_constraints = [
        ('uuid_uniq',
         'unique (uuid)',
         """UUIDs (Universally Unique IDentifier) for Sale Subscriptions must be unique!"""),
    ]

    @api.model
    def default_get(self, fields):
        res = super(SaleSubscription, self).default_get(fields)
        if 'code' in fields:
            res.update(code=self.env['ir.sequence'].next_by_code('sale.subscription') or 'New')
        return res

    @api.depends('rating_status', 'rating_status_period')
    def _compute_rating_request_deadline(self):
        periods = {'daily': 1, 'weekly': 7, 'bimonthly': 15, 'monthly': 30, 'quarterly': 90, 'yearly': 365}
        for r in self:
            r.rating_request_deadline = fields.datetime.now() + timedelta(days=periods.get(r.rating_status_period, 0))

    @api.depends('rating_ids.rating')
    def _compute_rating_percentage_satisfaction(self):
        for r in self:
            r.rating_percentage_satisfaction = -1

            activities = r.rating_get_grades()
            total_activity_values = sum(r.rating_get_grades().values())
            if total_activity_values and not float_is_zero(total_activity_values, precision_digits=16):
                r.rating_percentage_satisfaction = activities['great'] * 100 / total_activity_values

    def _compute_sale_order_count(self):
        OrderLine = self.env['sale.order.line']
        if OrderLine.check_access_rights('read', raise_exception=False):
            OrderLine = OrderLine.search([('subscription_id', 'in', self.ids)])
        OrderLine.read(['subscription_id', 'order_id'])

        for r in self:
            orders = OrderLine.filtered(lambda l: l.subscription_id == r).mapped('order_id')
            r.sale_order_count = orders and len(orders) or 0

    def _compute_is_favorite(self):
        for r in self:
            r.is_favorite = self.env.user in r.favorite_user_ids

    def _inverse_is_favorite(self):
        favorite_subscriptions = not_fav_subscriptions = self.env['sale.subscription'].sudo()
        for r in self:
            if self.env.user in r.favorite_user_ids:
                favorite_subscriptions |= r
            else:
                not_fav_subscriptions |= r
        not_fav_subscriptions.write({'favorite_user_ids': [(4, self.env.uid)]})
        favorite_subscriptions.write({'favorite_user_ids': [(3, self.env.uid)]})

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return stages.sudo().search([], order=order)

    def action_view_sales_orders(self):
        self.ensure_one()
        sales = self.env['sale.order'].search([('order_line.subscription_id', 'in', self.ids)])
        return {
            'name': _('Sales Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'views': [[self.env.ref('to_sale_subscription.sale_order_view_tree').id, 'tree'],
                      [self.env.ref('sale.view_order_form').id, 'form'],
                      [False, 'kanban'], [False, 'calendar'], [False, 'pivot'], [False, 'graph']],
            'domain': [['id', 'in', sales.ids]],
            'context': {'create': False},
        }

    def partial_invoice_line(self, sale_order, option_line, refund=False, date_from=False):
        """ Add an invoice line on the sales order for the specified option and add a discount
        to take the partial recurring period into account """
        order_line_obj = self.env['sale.order.line']
        values = {
            'order_id': sale_order.id,
            'product_id': option_line.product_id.id,
            'subscription_id': self.id,
            'product_uom_qty': option_line.quantity,
            'product_uom': option_line.uom_id.id,
            'discount': (1 - self.partial_recurring_invoice_ratio(date_from=date_from)) * 100,
            'price_unit': self.pricelist_id.with_context({'uom': option_line.uom_id.id}).get_product_price(option_line.product_id, 1, False),
            'name': option_line.name,
        }
        return order_line_obj.create(values)

    def partial_recurring_invoice_ratio(self, date_from=False):
        """Computes the ratio of the amount of time remaining in the current invoicing period
        over the total length of said invoicing period"""
        if date_from:
            date = fields.Date.to_date(date_from)
        else:
            date = fields.Date.today()
        if self.recurring_next_date == date:
            return 0
        invoicing_period = relativedelta(**{PERIODS[self.recurring_rule_type]: self.recurring_interval})
        recurring_next_invoice = self.recurring_next_date
        recurring_last_invoice = recurring_next_invoice - invoicing_period
        time_to_invoice = recurring_next_invoice - date - datetime.timedelta(days=1)
        interval = float((recurring_next_invoice - recurring_last_invoice).days)
        if float_is_zero(interval, precision_digits=16):
            return 0
        return float(time_to_invoice.days) / interval

    def _creation_subtype(self):
        return self.env.ref('to_sale_subscription.subtype_subscription_new')

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'stage_id' in init_values:
            return self.env.ref('to_sale_subscription.subtype_stage_change')
        return super(SaleSubscription, self)._track_subtype(init_values)

    def _compute_invoice_count(self):
        Invoice = self.env['account.move']
        can_read = Invoice.check_access_rights('read', raise_exception=False)
        for r in self:
            r.invoice_count = can_read and Invoice.search_count([('invoice_line_ids.subscription_id', '=', r.id)]) or 0

    @api.depends('line_ids', 'line_ids.quantity', 'line_ids.price_subtotal')
    def _compute_recurring_total(self):
        for r in self:
            r.recurring_total = sum(r.mapped('line_ids.price_subtotal'))

    @api.depends('recurring_total', 'template_id.recurring_interval', 'template_id.recurring_rule_type')
    def _compute_recurring_monthly(self):
        # Generally accepted ratios for monthly reporting
        interval_factor = {
            'daily': 30.0,
            'weekly': 30.0 / 7.0,
            'monthly': 1.0,
            'yearly': 1.0 / 12.0,
        }
        for r in self:
            r.recurring_monthly = (
                r.recurring_total * interval_factor[r.recurring_rule_type] / r.recurring_interval
            ) if r.template_id else 0

    @api.depends('uuid')
    def _compute_website_url(self):
        for r in self:
            r.website_url = '/my/subscriptions/%s/%s' % (r.id, r.uuid)

    @api.depends('line_ids', 'recurring_total')
    def _compute_amount_all(self):
        for r in self:
            r_sudo = r.sudo()
            price_total = tax_total = 0.0
            cur = r_sudo.pricelist_id.currency_id
            for line in r_sudo.line_ids:
                price_total += line.price_subtotal
                tax_total += line._amount_line_tax()
            r.recurring_amount_tax = cur.round(tax_total)
            r.recurring_amount_total = r.recurring_amount_tax + r.recurring_total

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.pricelist_id = self.partner_id.property_product_pricelist.id
        if self.partner_id.user_id:
            self.user_id = self.partner_id.user_id

    @api.onchange('template_id')
    def _onchange_template(self):
        if self.template_id:
            # Check if record is a new record or exists in db by checking its _origin
            # note that this property is not always set, hence the getattr
            if not getattr(self, '_origin', self.browse()) and not isinstance(self.id, int):
                self.description = self.template_id.description

    @api.model
    def _send_rating_all(self):
        subscriptions = self.search([])#self.search([('rating_status', '=', 'periodic'), ('rating_request_deadline', '<=', fields.Datetime.now())])
        for r in subscriptions:
            rating_template = r.stage_id.rating_template_id
            if rating_template:
                r.rating_send_request(rating_template, lang=r.partner_id.lang, force_send=False)
                r._compute_rating_request_deadline()
            self.env.cr.commit()

    def rating_apply(self, rate, token=None, feedback=None, subtype=None):
        return super(SaleSubscription, self).rating_apply(rate, token=token, feedback=feedback, subtype="to_sale_subscription.subtype_rating")

    def action_view_all_rating(self):
        """ return the action to see all the rating of the subscription, and activate default filters """
        self.ensure_one()
        if self.portal_show_rating:
            return {
                'type': 'ir.actions.act_url',
                'name': "Redirect to the Website Subscription Rating Page",
                'target': 'self',
                'url': "/subscription/rating/%s" % (self.id,)
            }
        action = self.env['ir.actions.act_window'].for_xml_id('to_sale_subscription', 'rating_rating_action_view')
        action['name'] = _('Ratings of %s') % (self.name,)
        action_context = safe_eval(action['context']) if action['context'] else {}
        action_context.update(self._context)
        action_context['search_default_parent_res_name'] = self.name
        action_context.pop('group_by', None)
        return dict(action, context=action_context)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['code'] = (
                vals.get('code') or
                self.env.context.get('default_code') or
                self.env['ir.sequence'].with_company(vals.get('company_id')).next_by_code('sale.subscription') or
                'New'
            )
            if vals.get('name', 'New') == 'New':
                vals['name'] = vals['code']
        res = super(SaleSubscription, self).create(vals_list)

        for r in res:
            if r.partner_id:
                r.message_subscribe(r.partner_id.ids)
        return res

    def write(self, vals):
        if vals.get('partner_id'):
            self.message_subscribe([vals['partner_id']])
        return super(SaleSubscription, self).write(vals)

    def unlink(self):
        self.wipe()
        self.env['sale.subscription.snapshot'].sudo().search([
            ('subscription_id', 'in', self.ids)]).unlink()
        return super(SaleSubscription, self).unlink()

    def _init_column(self, column_name):
        # to avoid generating a single default uuid when installing the module,
        # we need to set the default row by row for this column
        if column_name == "uuid":
            _logger.debug("Table '%s': setting default value of new column %s to unique values for each row",
                          self._table, column_name)
            self.env.cr.execute("SELECT id FROM %s WHERE uuid IS NULL" % self._table)
            acc_ids = self.env.cr.dictfetchall()
            query_list = [{'id': acc_id['id'], 'uuid': str(uuid4())} for acc_id in acc_ids]
            query = 'UPDATE ' + self._table + ' SET uuid = %(uuid)s WHERE id = %(id)s;'
            self.env.cr._obj.executemany(query, query_list)
            self.env.cr.commit()

        else:
            super(SaleSubscription, self)._init_column(column_name)

    def name_get(self):
        res = []
        for r in self:
            name = '%s - %s' % (r.code, r.partner_id.sudo().display_name) if r.code else r.partner_id.display_name
            if r.template_id.sudo().code:
                name = '%s/%s' % (r.template_id.sudo().code, name)
            res.append((r.id, name))
        return res

    def action_view_invoices(self):
        self.ensure_one()
        invoices = self.env['account.move'].search([('invoice_line_ids.subscription_id', 'in', self.ids)])
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        action["context"] = {"create": False}
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.model
    def cron_update_stage(self):
        today = fields.Date.today()
        next_month = fields.Date.to_string(fields.Date.from_string(today) + relativedelta(months=1))

        # set to pending if date is in less than a month
        domain_pending = [('date_end', '<', next_month), ('in_progress', '=', True)]
        subscriptions_pending = self.search(domain_pending)
        subscriptions_pending.set_to_renew()

        # set to close if date is passed
        domain_close = [('date_end', '<', today), '|', ('in_progress', '=', True), ('to_renew', '=', True)]
        subscriptions_close = self.search(domain_close)
        subscriptions_close.action_set_close()

        return dict(pending=subscriptions_pending.ids, closed=subscriptions_close.ids)

    @api.model
    def _cron_generate_recurring_invoice(self):
        return self._recurring_create_invoice(automatic=True)

    @api.model
    def _cron_update_sale_kpi(self):
        subscriptions = self.search([('in_progress', '=', True)])
        subscriptions._take_snapshot(fields.Date.today())
        subscriptions._compute_kpi()

    def _take_snapshot(self, date):
        for r in self:
            self.env['sale.subscription.snapshot'].create({
                'subscription_id': r.id,
                'date': fields.Date.to_string(date),
                'recurring_monthly': r.recurring_monthly,
            })

    def _get_subscription_delta(self, date):
        self.ensure_one()
        delta, percentage = False, False
        snapshot = self.env['sale.subscription.snapshot'].search([
            ('subscription_id', '=', self.id),
            ('date', '<=', date)], order='date desc', limit=1)
        if snapshot:
            delta = self.recurring_monthly - snapshot.recurring_monthly
            percentage = delta / snapshot.recurring_monthly
        return {'delta': delta, 'percentage': percentage}

    def _compute_kpi(self):
        for r in self:
            delta_1month = r._get_subscription_delta(fields.Date.today() - relativedelta(months=1))
            delta_3months = r._get_subscription_delta(fields.Date.today() - relativedelta(months=3))
            r.write({
                'kpi_1month_mrr_delta': delta_1month['delta'],
                'kpi_1month_mrr_percentage': delta_1month['percentage'],
                'kpi_3months_mrr_delta': delta_3months['delta'],
                'kpi_3months_mrr_percentage': delta_3months['percentage'],
            })

    def set_to_renew(self):
        return self.write({'to_renew': True})

    def action_set_close(self):
        Stage = self.env['sale.subscription.stage']
        for sub in self:
            stage = Stage.search([('in_progress', '=', False), ('sequence', '>=', sub.stage_id.sequence)], limit=1)
            if not stage:
                stage = Stage.search([('in_progress', '=', False)], limit=1)
            sub.write({'stage_id': stage.id, 'to_renew': False, 'date_end': fields.Date.today()})
        return True

    def set_open(self):
        Stage = self.env['sale.subscription.stage']
        for r in self:
            stage = Stage.search([('in_progress', '=', True), ('sequence', '>=', r.stage_id.sequence)], limit=1)
            if not stage:
                stage = Stage.search([('in_progress', '=', True)], limit=1)
            r.write({'stage_id': stage.id, 'to_renew': False, 'date_end': False})

    def _prepare_invoice_data(self):
        self.ensure_one()

        if not self.partner_id:
            raise UserError(_("Please select a Customer for Subscription %s!") % self.name)

        if 'force_company' in self.env.context:
            company = self.env['res.company'].browse(self.env.context['force_company'])
        else:
            company = self.company_id
            self = self.with_company(company).with_context(company_id=company.id)

        fpos_id = self.env['account.fiscal.position'].get_fiscal_position(self.partner_id.id)
        journal = self.template_id.journal_id or self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', company.id)], limit=1)
        if not journal:
            raise UserError(_('You must set a sale journal for the company "%s".') % (company.name or '',))

        next_date = fields.Date.from_string(self.recurring_next_date)
        if not next_date:
            raise UserError(_('You must set Date of Next Invoice of "%s".') % (self.display_name,))
        end_date = next_date + relativedelta(**{PERIODS[self.recurring_rule_type]: self.recurring_interval})
        end_date = end_date - relativedelta(days=1)  # remove 1 day as normal people thinks in term of inclusive ranges.
        addr = self.partner_id.address_get(['delivery', 'invoice'])

        sale_order = self.env['sale.order'].search([('order_line.subscription_id', 'in', self.ids)], order="id desc", limit=1)
        return {
            'type': 'out_invoice',
            'partner_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'currency_id': self.pricelist_id.currency_id.id,
            'journal_id': journal.id,
            'ref': self.code,
            'fiscal_position_id': fpos_id,
            'invoice_payment_term_id': sale_order.payment_term_id.id if sale_order else self.partner_id.property_payment_term_id.id,
            'company_id': company.id,
            'narration': _("This invoice covers the following period: %s - %s") % (format_date(self.env, next_date), format_date(self.env, end_date)),
            'user_id': self.user_id.id,
            'invoice_line_ids': self.line_ids._prepare_invoice_lines(fpos_id)
        }

    def action_recurring_create_invoice(self):
        self._recurring_create_invoice()
        return self.action_view_invoices()

    def _prepare_renewal_order_values(self):
        order_lines = []
        fpos_id = self.env['account.fiscal.position'].get_fiscal_position(self.partner_id.id)
        for line in self.line_ids:
            order_lines.append((0, 0, line._prepare_renewal_sale_order_line_vals()))
        addr = self.partner_id.address_get(['delivery', 'invoice'])
        sale_order = self.env['sale.order'].search([('order_line.subscription_id', 'in', self.ids)], order="id desc", limit=1)
        return {
            'pricelist_id': self.pricelist_id.id,
            'partner_id': self.partner_id.id,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'currency_id': self.pricelist_id.currency_id.id,
            'order_line': order_lines,
            'analytic_account_id': self.analytic_account_id.id,
            'subscription_state': 'renew',
            'origin': self.code,
            'note': self.description,
            'fiscal_position_id': fpos_id,
            'user_id': self.user_id.id,
            'payment_term_id': sale_order.payment_term_id.id if sale_order else self.partner_id.property_payment_term_id.id,
        }

    def action_prepare_renewal_order(self):
        self.ensure_one()
        order = self.env['sale.order'].create(self._prepare_renewal_order_values())
        order.order_line._compute_tax_id()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[False, "form"]],
            "res_id": order.id,
        }

    def increment_period(self):
        for subscription in self:
            current_date = subscription.recurring_next_date or self.default_get(['recurring_next_date'])['recurring_next_date']
            new_date = fields.Date.from_string(current_date) + relativedelta(**{PERIODS[subscription.recurring_rule_type]: subscription.recurring_interval})
            subscription.write({'recurring_next_date': new_date})

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', '|', ('code', operator, name), ('name', operator, name), ('partner_id.name', operator, name)]
        subscription_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return self.browse(subscription_ids).name_get()

    def wipe(self):
        """Wipe a subscription clean by deleting all its lines."""
        lines = self.mapped('line_ids')
        lines.unlink()
        return True

    def open_website_url(self):
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'self',
        }

    def add_option(self, option_id):
        pass

    def set_option(self, subscription, new_option, price):
        pass

    def remove_option(self, option_id):
        pass

    def _compute_options(self):
        pass

    # online payments
    def _do_payment(self, payment_token, invoice, two_steps_sec=True):
        self.ensure_one()
        reference = "SUB%s-%s" % (self.id, datetime.datetime.now().strftime('%y%m%d_%H%M%S'))
        values = {
            'amount': invoice.amount_total,
            'acquirer_id': payment_token.acquirer_id.id,
            'type': 'server2server',
            'currency_id': invoice.currency_id.id,
            'reference': reference,
            'payment_token_id': payment_token.id,
            'partner_id': self.partner_id.id,
            'partner_country_id': self.partner_id.country_id.id,
            'invoice_ids': [(6, 0, [invoice.id])],
            'callback_model_id': self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1).id,
            'callback_res_id': self.id,
            'callback_method': 'reconcile_pending_transaction',
        }

        tx = self.env['payment.transaction'].create(values)

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        payment_secure = {'3d_secure': two_steps_sec,
                          'accept_url': base_url + '/my/subscriptions/%s/payment/%s/accept/' % (self.uuid, tx.id),
                          'decline_url': base_url + '/my/subscriptions/%s/payment/%s/decline/' % (self.uuid, tx.id),
                          'exception_url': base_url + '/my/subscriptions/%s/payment/%s/exception/' % (self.uuid, tx.id),
                          }
        tx.s2s_do_transaction(**payment_secure)
        return tx

    def reconcile_pending_transaction(self, tx, invoice=False):
        self.ensure_one()
        if not invoice:
            invoice = tx.invoice_ids and tx.invoice_ids[0]
        if tx.state in ['done', 'authorized']:
            invoice.write({'reference': tx.reference, 'name': tx.reference})
            self.increment_period()
            self.set_open()
        else:
            invoice.action_cancel()
            invoice.unlink()

    def _recurring_create_invoice(self, automatic=False):
        auto_commit = self.env.context.get('auto_commit', True)
        cr = self.env.cr
        invoices = self.env['account.move']
        current_date = fields.Date.today()
        IrModelData = self.env['ir.model.data']
        MailTemplate = self.env['mail.template']
        if len(self) > 0:
            subscriptions = self
        else:
            domain = [('recurring_next_date', '<=', current_date),
                      '|', ('in_progress', '=', True), ('to_renew', '=', True)]
            subscriptions = self.search(domain)
        if subscriptions:
            sub_data = subscriptions.read(fields=['id', 'company_id'])
            for company_id in set(data['company_id'][0] for data in sub_data):
                sub_ids = [s['id'] for s in sub_data if s['company_id'][0] == company_id]
                subs = self.with_company(company_id).with_context(company_id=company_id).browse(sub_ids)
                context_company = dict(self.env.context, company_id=company_id, force_company=company_id)
                for subscription in subs:
                    subscription = subscription[0]  # Trick to not prefetch other subscriptions, as the cache is currently invalidated at each iteration
                    if automatic and auto_commit:
                        cr.commit()
                    # payment + invoice (only by cron)
                    if subscription.template_id.payment_mode in ['validate_send_payment', 'success_payment'] and subscription.recurring_total and automatic:
                        try:
                            payment_token = subscription.payment_token_id
                            tx = None
                            if payment_token:
                                invoice_values = subscription.with_context(lang=subscription.partner_id.lang)._prepare_invoice_data()
                                new_invoice = self.env['account.move'].with_context(context_company).create(invoice_values)
                                new_invoice.message_post_with_view(
                                    'mail.message_origin_link',
                                    values={'self': new_invoice, 'origin': subscription},
                                    subtype_id=self.env.ref('mail.mt_note').id)
                                tx = subscription._do_payment(payment_token, new_invoice, two_steps_sec=False)[0]
                                # commit change as soon as we try the payment so we have a trace somewhere
                                if auto_commit:
                                    cr.commit()
                                if tx.state in ['done', 'authorized']:
                                    subscription.send_success_mail(tx, new_invoice)
                                    msg_body = 'Automatic payment succeeded. Payment reference: <a href=# data-oe-model=payment.transaction data-oe-id=%d>%s</a>; Amount: %s. Invoice <a href=# data-oe-model=account.move data-oe-id=%d>View Invoice</a>.' % (tx.id, tx.reference, tx.amount, new_invoice.id)
                                    subscription.message_post(body=msg_body)
                                    if subscription.template_id.payment_mode == 'validate_send_payment':
                                        subscription.validate_and_send_invoice(new_invoice)
                                    if auto_commit:
                                        cr.commit()
                                else:
                                    _logger.error('Cannot generate recurring invoice for the subscription %s', subscription.code)
                                    if auto_commit:
                                        cr.rollback()
                                    new_invoice.unlink()
                            if tx is None or tx.state != 'done':
                                amount = subscription.recurring_total
                                date_close = (
                                    subscription.recurring_next_date +
                                    relativedelta(days=subscription.template_id.closed_automatically_after or 30)
                                )
                                ctx = dict(self.env.context or {})
                                ctx.update(subscription._prepare_ctx_send_mail_vals(False, amount, date_close=date_close))

                                close_subscription = current_date >= date_close
                                if close_subscription:
                                    _, template_id = IrModelData.get_object_reference('to_sale_subscription', 'email_payment_close')
                                    template = MailTemplate.browse(template_id)
                                    template.with_context(ctx).send_mail(subscription.id)
                                    _logger.debug("Cannot send subscription by email to %s for subscription %s and close subscription", subscription.partner_id.email, subscription.id)
                                    msg_body = "Subscription closed automatically. Because, we cannot payment automatically after multiple attempts"
                                    subscription.message_post(body=msg_body)
                                    subscription.action_set_close()
                                else:
                                    _, template_id = IrModelData.get_object_reference('to_sale_subscription', 'email_payment_reminder')
                                    msg_body = "Subscription set to 'To Renew'. Because cannot payment automatically."
                                    if (fields.Date.today() - subscription.recurring_next_date).days in [0, 3, 7, 14]:
                                        template = MailTemplate.browse(template_id)
                                        template.with_context(ctx).send_mail(subscription.id)
                                        _logger.debug("Cannot send payment by email to %s for subscription %s and seting subscription to pending", subscription.partner_id.email, subscription.id)
                                        msg_body += ' Email sent to customer.'
                                    subscription.message_post(body=msg_body)
                                    subscription.set_to_renew()
                            if auto_commit:
                                cr.commit()
                        except Exception:
                            if auto_commit:
                                cr.rollback()
                            # we assume that the payment is run only once a day
                            traceback_message = traceback.format_exc()
                            _logger.error(traceback_message)
                            last_tx = self.env['payment.transaction'].search([('reference', 'like', 'SUBSCRIPTION-%s-%s' % (subscription.id, fields.Date.today().strftime('%y%m%d')))], limit=1)
                            error_message = "Something wrong when renewal of subscription %s (%s)" % (subscription.code, 'Payment: %s' % last_tx.reference if last_tx and last_tx.state == 'done' else 'No payment.')
                            _logger.error(error_message)

                    # invoice only
                    elif subscription.template_id.payment_mode in ['draft_invoice', 'manual', 'validate_send']:
                        try:
                            invoice_values = subscription.with_context(lang=subscription.partner_id.lang)._prepare_invoice_data()
                            new_invoice = self.env['account.move'].with_context(context_company).create(invoice_values)
                            new_invoice.message_post_with_view(
                                'mail.message_origin_link',
                                values={'self': new_invoice, 'origin': subscription},
                                subtype_id=self.env.ref('mail.mt_note').id)
                            invoices += new_invoice
                            next_date = subscription.recurring_next_date or current_date
                            invoicing_period = relativedelta(**{PERIODS[subscription.recurring_rule_type]: subscription.recurring_interval})
                            new_date = next_date + invoicing_period
                            subscription.write({'recurring_next_date': new_date.strftime('%Y-%m-%d')})
                            if subscription.template_id.payment_mode == 'validate_send':
                                subscription.validate_and_send_invoice(new_invoice)
                            if automatic and auto_commit:
                                cr.commit()
                        except Exception:
                            if automatic and auto_commit:
                                cr.rollback()
                                _logger.exception('Cannot generate recurring invoice for subscription %s', subscription.code)
                            else:
                                raise
        return invoices

    def send_success_mail(self, tx, invoice):
        next_date = self.recurring_next_date or fields.Date.today()
        # if no recurring next date, have next invoice be today + interval
        if not self.recurring_next_date:
            invoicing_period = relativedelta(**{PERIODS[self.recurring_rule_type]: self.recurring_interval})
            next_date = next_date + invoicing_period
        _, template_id = self.env['ir.model.data'].get_object_reference('to_sale_subscription', 'email_payment_success')
        ctx = dict(self.env.context or {})
        ctx.update(self._prepare_ctx_send_mail_vals(True, tx.amount, next_date=next_date))
        _logger.debug("Send payment confirmation by email to %s for subscription %s", self.partner_id.email, self.id)
        template = self.env['mail.template'].browse(template_id)
        return template.with_context(ctx).send_mail(invoice.id)

    def _prepare_ctx_send_mail_vals(self, renewed, amount, next_date=False, date_close=False):
        self.ensure_one()
        return {
            'payment_token': self.payment_token_id and self.payment_token_id.name or '',
            'renewed': renewed,
            'total_amount': amount,
            'next_date': next_date or fields.Date.today(),
            'previous_date': self.recurring_next_date,
            'email_to': self.partner_id.email,
            'code': self.code,
            'currency': self.pricelist_id.currency_id.name,
            'date_end': self.date_end,
            'date_close': date_close or fields.Date.today(),
        }

    def validate_and_send_invoice(self, invoice):
        self.ensure_one()
        invoice.post()
        ctx = dict(self.env.context or {})
        ctx.update(self._prepare_ctx_send_mail_vals(False, invoice.amount_total))
        _logger.debug("Send invoice by email to %s for subscription %s", self.partner_id.email, self.id)
        self.template_id.invoice_mail_template_id.with_context(ctx).send_mail(invoice.id)

    def _prepare_payment_token_linked_record_data(self):
        self.ensure_one()
        return {
            'description': self._description,
            'id': self.id,
            'name': self.name,
            'url': '/my/subscriptions/%s/%s' % (str(self.id), str(self.uuid)),
            }
