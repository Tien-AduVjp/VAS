from odoo import models, fields, api
from odoo.osv import expression


class Wallet(models.Model):
    _name = 'wallet'
    _description = 'Wallet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'

    currency_id = fields.Many2one('res.currency', required=True, readonly=True)
    partner_id = fields.Many2one('res.partner', required=True, readonly=True)
    amount = fields.Monetary(currency_field='currency_id', compute='_compute_amount', store=True, tracking=True)
    payment_ids = fields.One2many('account.payment', 'wallet_id', groups="account.group_account_invoice")
    payments_count = fields.Integer(compute='_compute_payments_count', groups="account.group_account_invoice")
    transaction_ids = fields.One2many('payment.transaction', 'wallet_id', readonly=True)
    move_line_ids = fields.One2many('account.move.line', 'wallet_id', string='Journal Items', readonly=True, groups="account.group_account_invoice")
    move_lines_count = fields.Integer(string='Journal Items Count', compute='_compute_move_lines_count', compute_sudo=True)
    empty_date = fields.Datetime(string='Est. Credit out',
                                 compute='_compute_empty_date', store=True,
                                 help='Estimated date on when the wallet is empty')
    realtime_amount = fields.Monetary(string='Realtime Amount', currency_field='currency_id',
                                      compute='_compute_realtime_amount', compute_sudo=True)

    _sql_constraints = [
        ('currency_per_partner_uniq', 'unique(currency_id, partner_id)', 'Wallet Error. Currency must be unique per partner.')
    ]

    @api.depends('amount')
    def _compute_realtime_amount(self):
        for r in self:
            r.realtime_amount = r._get_realtime_amount()

    def _get_realtime_amount(self):
        self.ensure_one()
        return self.amount

    @api.depends('move_line_ids.reconciled',
                 'move_line_ids.move_id.state',
                 'move_line_ids.currency_id',
                 'move_line_ids.company_currency_id',
                 'move_line_ids.account_id.internal_type',
                 'move_line_ids.wallet_amount_residual',
                 'move_line_ids.wallet_amount_residual_currency')
    def _compute_amount(self):
        all_move_lines = self.env['account.move.line'].search([
            ('reconciled', '=', False),
            ('wallet_id', 'in', self.ids),
            ('account_id.internal_type', '=', 'receivable'),
            ('move_id.state', '=', 'posted')
        ])
        for r in self:
            amount = 0
            move_lines = all_move_lines.filtered(lambda l: l.wallet_id == r)
            for line in move_lines:
                if r.currency_id == line.company_currency_id:
                    amount += line.wallet_amount_residual
                elif r.currency_id == line.currency_id:
                    amount += line.wallet_amount_residual_currency
                else:
                    rate = line.payment_id._get_wallet_currency_conversion_rate()
                    if rate:
                        amount += line.wallet_amount_residual * rate
            r.amount = -amount

    def _compute_move_lines_count(self):
        total_data = self.env['account.move.line'].read_group([('wallet_id', 'in', self.ids)], ['wallet_id'], ['wallet_id'])
        mapped_data = dict([(dict_data['wallet_id'][0], dict_data['wallet_id_count']) for dict_data in total_data])
        for r in self:
            r.move_lines_count = mapped_data.get(r.id, 0)

    @api.depends('amount')
    def _compute_empty_date(self):
        for r in self:
            r.empty_date = r._get_empty_date()

    def _get_empty_date(self):
        """
        This method is place holder for other module to override
        to calculate empty date of this wallet
        """
        return False

    @api.depends('payment_ids')
    def _compute_payments_count(self):
        for r in self:
            r.payments_count = len(r.payment_ids)

    def get_payment_acquirers(self):
        self.ensure_one()
        domain = self._get_payment_acquires_domain()
        return self.env['payment.acquirer'].search(domain)

    def _get_payment_acquires_domain(self):
        self.ensure_one()
        return expression.AND([
            ['&', ('state', 'in', ['enabled', 'test']), ('company_id', '=', self.env.company.id)],
            ['|', ('country_ids', '=', False), ('country_ids', 'in', [self.partner_id.country_id.id])]
        ])

    def _prepare_payment_transaction_values(self, acquirer, amount, **kwargs):
        values = dict(
            acquirer_id=acquirer.id,
            amount=amount,
            wallet_amount=amount,
            currency_id=self.currency_id.id,
            partner_id=self.partner_id.id,
            wallet_id=self.id
        )
        values.update(**kwargs)
        return values

    def create_payment_transaction(self, acquirer, amount, **kwargs):
        values = self._prepare_payment_transaction_values(acquirer, amount, **kwargs)
        return self.env['payment.transaction'].create(values)

    def action_view_account_move_lines(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_moves_all')
        action['context'] = {'search_default_posted':1, 'search_default_receivable':1}
        action['domain'] = "[('wallet_id', 'in', %s)]" % self.ids
        return action

    def get_last_transaction(self):
        return self.transaction_ids.sorted('id', reverse=True)[:1]

    def name_get(self):
        vals = []
        for r in self:
            name = '{} ({})'.format(r.partner_id.commercial_partner_id.display_name, r.currency_id.display_name)
            vals.append((r.id, name))
        return vals
