from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
from odoo.tools.misc import format_amount


class CustomDeclarationPayment(models.TransientModel):
    _name = 'custom.declaration.payment'
    _description = 'Custom Declaration Payment Wizard'

    @api.model
    def _get_default_journal(self):
        company_id = self._context.get('company_id', self.env.company.id)
        domain = [
            ('type', 'in', ('cash', 'bank')),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)

    @api.model
    def _get_default_custom_dec_import_id(self):
        res = False
        active_model = self._context.get('active_model', False)
        if active_model == 'custom.declaration.import':
            active_id = self._context.get('active_id', False)
            if active_id:
                res = self.env[active_model].browse(active_id)
        return res

    @api.model
    def _get_default_custom_dec_export_id(self):
        res = False
        active_model = self._context.get('active_model', False)
        if active_model == 'custom.declaration.export':
            active_id = self._context.get('active_id', False)
            if active_id:
                res = self.env[active_model].browse(active_id)
        return res

    custom_dec_import_id = fields.Many2one('custom.declaration.import', string='Import Custom Declaration', default=lambda self: self._get_default_custom_dec_import_id())
    custom_dec_export_id = fields.Many2one('custom.declaration.export', string='Export Custom Declaration', default=lambda self: self._get_default_custom_dec_export_id())
#     import_tax_ids = fields.Many2many('custom.declaration.tax.import', string='Import Tax')
#     export_tax_ids = fields.Many2many('custom.declaration.tax.export', string='Export Tax')
    partner_id = fields.Many2one('res.partner', string='Partner', required=True,
                                 domain="[('id', 'in', available_partner_ids)]")
    payment_date = fields.Date(string="Payment Date", required=True, default=fields.Date.today)
    journal_id = fields.Many2one('account.journal', string="Payment Method",
                                 required=True, domain=[('type', 'in', ('cash', 'bank'))], default=_get_default_journal)
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', required=True,
                                        domain="[('id', 'in', available_payment_method_ids)]")
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', compute='_compute_currency_id', store=True)
    communication = fields.Char(string='Memo')
    available_partner_ids = fields.Many2many('res.partner', compute='_compute_available_partner_ids',
                                             string='Available Partners',
                                             help="Technical field to filter partner based on selected custom declaration")
    available_payment_method_ids = fields.Many2many('account.payment.method', compute='_compute_available_payment_method_ids',
                                             string='Available Payment Methods',
                                             help="Technical field to filter payment method based on selected journal")

    _sql_constraints = [
        ('amount_positive_check',
         'CHECK(amount > 0.0)',
         "The amount must be greater than zero!"),
    ]

    @api.constrains('custom_dec_import_id', 'custom_dec_export_id')
    def _check_custom_dec_import_vs_custom_dec_export(self):
        for r in self:
            if r.custom_dec_import_id and r.custom_dec_export_id:
                raise ValidationError(_("You cannot make tax payment for both Import Custom Declaration and Export Custom Declaration at the same time"))
            elif not r.custom_dec_import_id and not r.custom_dec_export_id:
                raise ValidationError(_("Unknown Import Custom Declaration and Export Custom Declaration for tax payment"))

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        unreconcile_tax_aml_ids = self.get_unreconcile_tax_aml()
        self.amount = abs(sum(unreconcile_tax_aml_ids.mapped('amount_residual')))

    @api.onchange('custom_dec_import_id', 'custom_dec_export_id')
    def _onchange_custom_declaration(self):
        res = {}
        if not self.custom_dec_import_id and not self.custom_dec_export_id:
            return res
        partner_ids = self.env['res.partner']
        if self.custom_dec_import_id:
            partner_ids = self.custom_dec_import_id.tax_line_ids.filtered(lambda r: not r.paid).mapped('partner_id')
        elif self.custom_dec_export_id:
            partner_ids = self.custom_dec_export_id.tax_line_ids.filtered(lambda r: not r.paid).mapped('partner_id')

        self.partner_id = partner_ids[0]
        return res

    @api.depends('custom_dec_import_id', 'custom_dec_export_id')
    def _compute_available_partner_ids(self):
        for r in self:
            if r.custom_dec_import_id:
                r.available_partner_ids = r.custom_dec_import_id.tax_line_ids.filtered(lambda l: not l.paid).mapped('partner_id')
            elif r.custom_dec_export_id:
                r.available_partner_ids = r.custom_dec_export_id.tax_line_ids.filtered(lambda l: not l.paid).mapped('partner_id')
            else:
                r.available_partner_ids = self.env['res.partner']

    @api.depends('journal_id')
    def _compute_hide_payment_method(self):
        for r in self:
            if not r.journal_id:
                r.hide_payment_method = True
                return
            journal_payment_methods = r.journal_id.outbound_payment_method_ids
            r.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

    @api.depends('journal_id.currency_id', 'company_id.currency_id')
    def _compute_currency_id(self):
        for r in self:
            r.currency_id = r.journal_id.currency_id if r.journal_id.currency_id else r.company_id.currency_id

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False

    @api.depends('journal_id')
    def _compute_available_payment_method_ids(self):
        for r in self:
            if r.journal_id:
                r.available_payment_method_ids = r.journal_id.outbound_payment_method_ids
            else:
                r.available_payment_method_ids = self.env['account.payment.method'].search([('payment_type', '=', 'outbound')])

    @api.model
    def get_unreconcile_tax_aml(self):
        tax_aml_ids = self.env['account.move.line']
        if self.custom_dec_import_id:
            tax_aml_ids += self.custom_dec_import_id.get_unreconcile_tax_aml()
        elif self.custom_dec_export_id:
            tax_aml_ids += self.custom_dec_export_id.get_unreconcile_tax_aml()
        return tax_aml_ids

    def action_account_move_create(self):
        """
        This method will search all account move lines that contain tax and and in due
        then create an account move that will reconcile those lines
        """
        self.ensure_one()
        precision_rounding = self.company_id.currency_id.rounding
        account_move_line_ids = []
        tax_aml_ids = self.get_unreconcile_tax_aml()
        ref = "TAX.PAY/"
        if self.custom_dec_import_id:
            ref += self.custom_dec_import_id.name
        elif self.custom_dec_export_id:
            ref += self.custom_dec_export_id.name

        abs_amount_residual = abs(sum(tax_aml_ids.mapped('amount_residual')))
        if float_compare(abs(self.amount), abs_amount_residual, precision_rounding=precision_rounding) == 1:
            raise ValidationError(_("The payment amount must not be greater than the total due amount which is %s only. You might be trying to pay"
                                    " for the taxes that are already paid, or some tax accounts do not allow reconcile.")
                                  % (format_amount(self.env, abs_amount_residual, self.company_id.currency_id, lang_code=False)))

        amount = self.amount
        credit = 0.0
        for tax_repartition_line in tax_aml_ids.mapped('tax_repartition_line_id'):
            tax_line_id = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
            aml_ids = tax_aml_ids.filtered(lambda l: l.tax_line_id.id == tax_line_id.id)
            for account_id in aml_ids.mapped('account_id'):
                if not account_id.reconcile:
                    raise ValidationError(_("The account '%s' must be allowed to reconcile."))
                acc_aml_ids = aml_ids.filtered(lambda l: l.account_id.id == account_id.id)
                debit_tax_line = {
                    'date_maturity': self.payment_date,
                    'partner_id': self.partner_id.id,
                    'name': ref,
                    'debit': 0.0,
                    'credit': 0.0,
                    'tax_repartition_line_id': tax_repartition_line.id,
                    'account_id': account_id.id,
                    'ref': ref,
                    'quantity': 1,
                    }
                for aml_id in acc_aml_ids:
                    abs_amount_residual = abs(aml_id.amount_residual)
                    if float_compare(abs(amount), abs(aml_id.amount_residual), precision_rounding=precision_rounding) >= 0:
                        debit_tax_line['debit'] += abs_amount_residual
                        credit += abs_amount_residual
                        # amount -= aml_id.amount_residual
                        amount -= abs_amount_residual
                    else:
                        debit_tax_line['debit'] += abs(amount)
                        credit += abs(amount)
                        amount = 0.0

                account_move_line_ids.append((0, 0, debit_tax_line))

        if account_move_line_ids:
            # append liquidity line
            account_move_line_ids.append((0, 0, {
                    'date_maturity': self.payment_date,
                    'partner_id': self.partner_id.id,
                    'name': ref,
                    'debit': 0.0,
                    'credit': credit,
                    'account_id': self.journal_id.payment_credit_account_id.id,
                    'ref': ref,
                    'quantity': 1,

                }))

            vals = {
                'journal_id': self.journal_id.id,
                'company_id': self.company_id.id,
                'date': self.payment_date,
                'ref': ref,
                'line_ids': account_move_line_ids,
            }
            if self.custom_dec_import_id:
                vals['custom_declaration_import_id'] = self.custom_dec_import_id.id
            elif self.custom_dec_export_id:
                vals['custom_declaration_export_id'] = self.custom_dec_export_id.id

            move = self.env['account.move'].create(vals)
            move._post()
            lines_to_reconcile = (move.line_ids.filtered(lambda l: l.tax_line_id) + tax_aml_ids).filtered(lambda l: not l.full_reconcile_id)
            # group lines based on account to reconcile
            lines_by_account = {}
            for line in lines_to_reconcile:
                if lines_by_account.get(line.account_id.id, False):
                    lines_by_account[line.account_id.id] |= line
                else:
                    lines_by_account[line.account_id.id] = line
            for line_group in lines_by_account.values():
                line_group.reconcile()

    def action_pay(self):
        self.ensure_one()
        # Create account move and post it then reconcile tax lines
        self.action_account_move_create()
        return {'type': 'ir.actions.act_window_close'}
