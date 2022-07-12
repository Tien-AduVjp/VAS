from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class AbstractCustomDeclaration(models.AbstractModel):
    _name = 'abstract.custom.declaration'
    _order = 'request_date desc, id desc'
    _description = 'Contains the logic shared between models'

    STATES = [
        ('draft', 'Draft'),
        ('open', 'Waiting Confirmation by Custom'),
        ('confirm', 'Confirmed by Custom'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ]

    @api.model
    def _default_journal(self):
        journal_id = self.company_id.account_journal_custom_clearance \
        or self.env['account.journal'].search([('code', '=', 'CDJ'), ('company_id', '=', self.company_id.id)], limit=1)
        return journal_id.id or False

    name = fields.Char(string="Internal Reference", required=True, copy=False, readonly=True, index=True, default='/')
    partner_id = fields.Many2one('res.partner', string="Custom Authority", required=True,
                                 readonly=True, states={'draft': [('readonly', False)]})

    number = fields.Char(string="Custom Doc. Number", help="The document number that provided by Custom Authority")
    request_date = fields.Date(string="Request Date", default=fields.Date.context_today)
    clearance_date = fields.Date(string="Clearance Date",
                                 help='The date on which the custom declaration request is accepted and cleared.'
                                 ' Leave it empty to use the current date upon confirmation by the custom authority is set.',
                                 states={'confirm': [('readonly', True)],
                                         'done': [('readonly', True)],
                                         'cancel': [('readonly', True)]})
    journal_id = fields.Many2one('account.journal', string="Custom Clearance Journal", default=_default_journal, required=True)
    state = fields.Selection(STATES, string="Status", index=True, readonly=True,
                             tracking=True, copy=False, default='draft', required=True)

    invoice_id = fields.Many2one('account.move', string='Invoice', domain="[('id', 'in', available_invoice_ids)]")

    stock_picking_ids = fields.Many2many('stock.picking', string="Transfers", required=True,
                                       readonly=True, states={'draft': [('readonly', False)]},
                                       domain="[('id', 'in', available_picking_ids)]")

    picking_type_id = fields.Many2one('stock.picking.type', string='Transfer Type', compute='_compute_common_data', compute_sudo=True)

    company_id = fields.Many2one('res.company', string='Company', compute='_compute_common_data', store=True)

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  readonly=True, compute="_compute_currency_id", store=True,
                                  default=lambda self: self.env.company.currency_id)

    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Company Currency', readonly=True,
        help='Utility field to express amount currency', store=True)

    currency_rate = fields.Float(string='Currency Rate', required=True,
                                 help='The rate to the company\'s currency applied when computing taxes', digits='Account')
    show_currency_rate = fields.Boolean(string='Show Currency Rate', compute='_compute_show_currency_rate')

    amount_tax = fields.Monetary(string='Total Taxes', store=True, compute='_compute_tax',
                                 tracking=True, currency_field='company_currency_id')

    currency_amount_tax = fields.Monetary(string='Total Currency Taxes', store=True,
                                          compute='_compute_tax_currency', currency_field='currency_id')

    total_cost = fields.Monetary(string='Total Taxable Value', store=True, compute='_compute_total_cost',
                                 currency_field='company_currency_id')

    total_cost_currency = fields.Monetary(string='Total Taxable Value Currency', store=True, compute='_compute_total_cost_currency',
                                          currency_field='currency_id')
    is_paid = fields.Boolean(string='Is Paid', compute='_compute_is_paid')
    compute_tax_lines_onfly = fields.Boolean(string='On-fly Taxes Computation', default=True,
                                             help="If checked, upon changing data in the Operations table, Odoo will immediately"
                                             " recompute taxes table accordingly, that may introduce bad performance when you"
                                             " have a lot of taxes and products in the Operations table. In such case, you may want"
                                             " to disble on-fly taxes computation by unchecking this box. After disabling, you will"
                                             " need to hit Compute Tax Lines to get the computation done.")
    available_picking_ids = fields.Many2many('stock.picking', compute='_compute_available_data_based_on_selected_order',
                                             string='Available Transfers',
                                             help="Technical field to filter transfers based on selected order and transfer")
    available_invoice_ids = fields.Many2many('account.move', compute='_compute_available_data_based_on_selected_order',
                                             string='Available Invoices',
                                             help="Technical field to filter invoices based on selected order")

    @api.depends('stock_picking_ids')
    def _compute_common_data(self):
        for r in self:
            picking_types = r.stock_picking_ids.picking_type_id
            companies = r.stock_picking_ids.company_id
            if picking_types:
                r.picking_type_id = picking_types[0]
            else:
                r.picking_type_id = False
            if companies:
                r.company_id = companies[0]
            else:
                r.company_id = False

    @api.model_create_multi
    def create(self, vals_list):
        recs = super(AbstractCustomDeclaration, self).create(vals_list)
        recs.mapped('tax_line_ids').generate_custom_declaration_tax_groups()
        for r in recs:
            for tax_line_id in r.tax_line_ids:
                dec_lines = r.custom_declaration_line_ids.filtered(lambda line:
                                                                   tax_line_id.product_id == line.product_id and
                                                                   tax_line_id.tax_id.id in line.tax_ids.ids and
                                                                   tax_line_id.stock_move_id == line.stock_move_id)
                tax_line_id.custom_declaration_line_id = dec_lines and dec_lines[0].id or False
        return recs

    def write(self, vals):
        generate_tax_group = 'tax_line_ids' in vals
        res = super(AbstractCustomDeclaration, self).write(vals)
        if generate_tax_group:
            custom_dec_tax_group_ids = self.mapped('custom_dec_tax_group_ids')
            if custom_dec_tax_group_ids:
                custom_dec_tax_group_ids.unlink()
            self.mapped('tax_line_ids').generate_custom_declaration_tax_groups()
        return res

    @api.constrains('stock_picking_ids')
    def _check_stock_pickings(self):
        for r in self:
            # check pickings has same picking type
            picking_types = r.stock_picking_ids.picking_type_id
            if len(picking_types) > 1:
                raise ValidationError(_("Selected pickings doesn't have same picking type, please check again."))

            # check picking has same company
            companies = r.stock_picking_ids.company_id
            if len(companies) > 1:
                raise ValidationError(_("Selected pickings doesn't have same company, please check again."))

            # check product in each stock move
            for move in r.stock_picking_ids.move_lines:
                if move.product_id.valuation != 'real_time' or move.product_id.cost_method not in ['fifo', 'average']:
                    raise ValidationError(_("The product '%s' of the transfer '%s' must be configured in automated valuation with"
                                            " FIFO or AVCO costing method")
                                            % (move.product_id.display_name, move.picking_id.name))

    @api.depends('currency_id', 'company_currency_id')
    def _compute_show_currency_rate(self):
        for r in self:
            r.show_currency_rate = r.currency_id.id != r.company_currency_id.id

    def _prepare_custom_declaration_lines_data(self):
        raise ValidationError(_("The method `_prepare_custom_declaration_lines_data()` has not been implemented for the model %s") % (self._name,))

    @api.onchange('stock_picking_ids')
    def _onchange_stock_picking_ids(self):
        if self.company_id:
            self.journal_id = self.company_id.account_journal_custom_clearance
        res = self._prepare_custom_declaration_lines_data()
        if not 'warning' in res:
            self.custom_declaration_line_ids = res
            return {}
        else:
            return res

    @api.onchange('currency_rate', 'company_id', 'request_date')
    def _onchange_dates_and_rate(self):
        if self.custom_declaration_line_ids:
            self.custom_declaration_line_ids.update({'currency_rate': self.currency_rate})
            self._onchange_custom_declaration_line_ids()

    def unlink(self):
        if any(request.state not in ['draft'] for request in self):
            raise UserError(_('You can only delete a draft record!'))
        return super(AbstractCustomDeclaration, self).unlink()

    def action_done(self):
        for r in self:
            if r.state != 'confirm':
                raise UserError(_("You cannot set done for the declaration '%s' while its state is not 'Confirmed by Custom'") % (r.name,))
        self.write({'state':'done'})

    def action_cancel(self):
        for r in self:
            posted_laned_costs = r.landed_cost_ids.filtered(lambda x: x.state == 'done')
            if posted_laned_costs:
                raise ValidationError(_("Could not cancel the document `%s` while the following referenced"
                                        " landed costs are posted: %s\n")
                                      % (r.name, ', '.join(posted_laned_costs.mapped('name'))))
        self.mapped('landed_cost_ids').unlink()

        account_move_ids = self.mapped('account_move_ids')
        draft_moves = account_move_ids.filtered(lambda m: m.state == 'draft')
        non_draft_moves = account_move_ids - draft_moves
        if draft_moves:
            draft_moves.unlink()
        if non_draft_moves:
            non_draft_moves.button_cancel()
            non_draft_moves.unlink

        self.write({'state':'cancel'})

    def action_draft(self):
        self.write({'state':'draft'})

    def _compute_currency_id(self):
        raise ValidationError(_("The method `_compute_currency_id()` has not been implemented for the model `%s`") % self._name)

    def _compute_available_data_based_on_selected_order(self):
        raise ValidationError(_("The method `_compute_available_data_based_on_selected_order()` "
                                "has not been implemented for the model `%s`") % self._name)

    @api.onchange('currency_id', 'request_date', 'clearance_date')
    def _get_currency_rate(self):
        date = self.clearance_date or self.request_date or fields.Date.today()
        company_id = self.company_id or self.env.company
        if self.currency_id:
            self.currency_rate = self.env['res.currency']._get_conversion_rate(self.currency_id, company_id.currency_id, company_id, date)
        else:
            self.currency_rate = 1.0

    def _set_currency_rate(self):
        pass

    @api.depends('amount_tax', 'currency_rate')
    def _compute_tax_currency(self):
        for r in self:
            if not float_is_zero(r.currency_rate, precision_digits=16):
                r.currency_amount_tax = r.amount_tax / r.currency_rate
            else:
                r.currency_amount_tax = r.amount_tax

    @api.depends('custom_declaration_line_ids', 'custom_declaration_line_ids.total_cost_currency',
                 'custom_declaration_line_ids.extra_expense_currency')
    def _compute_total_cost_currency(self):
        for r in self:
            if r.custom_declaration_line_ids:
                r.total_cost_currency = sum(r.custom_declaration_line_ids.mapped('total_cost_currency')) \
                                        + sum(r.custom_declaration_line_ids.mapped('extra_expense_currency'))

    @api.depends('tax_line_ids', 'tax_line_ids.amount')
    def _compute_tax(self):
        for r in self:
            r.amount_tax = sum(r.tax_line_ids.mapped('amount'))

    @api.depends('total_cost_currency', 'currency_rate')
    def _compute_total_cost(self):
        for r in self:
            r.total_cost = r.total_cost_currency * r.currency_rate

    def action_open(self):
        for r in self:
            exists_requested_pickings = r._get_exists_requested_pickings()
            if exists_requested_pickings:
                raise UserError(_("Custom clearance document for transfer `%s` exists.\n You should either get back to work on that"
                                  " document(s) or cancel / delete it.")
                                % (','.join(exists_requested_pickings.mapped('name'))))

            if not r.custom_declaration_line_ids:
                raise UserError(_('Please create some operations.'))

            un_completed_pickings = r.stock_picking_ids.filtered(lambda pk: pk.state != 'done')
            if un_completed_pickings:
                raise UserError(_("Please validate the transfer `%s` before you can open this request!")
                                % (','.join(un_completed_pickings.mapped('name'))))

            inconsistent_pickings = r._get_inconsistent_pickings()
            if inconsistent_pickings:
                raise UserError(_("The transfer `%s` is not consistent with content of declaration. "
                                  "Please remove transfer(s) from custom declaration and select them again to update latest data!")
                                 % (','.join(inconsistent_pickings.mapped('name'))))

            r.write({
                'state':'open',
                'request_date': r.request_date or fields.Date.today()
                })

    def action_confirm(self):
        for r in self:
            if not r.journal_id:
                raise UserError(_('Please select a custom clearance journal before you can confirm it.'))
            if r.state != 'open':
                raise UserError(_("You cannot confirm the declaration '%s' while its state is not 'Waiting Confirmation by Custom'") % (r.name,))
            update_data = {
                'state':'confirm',
                }
            if not r.clearance_date:
                update_data['clearance_date'] = fields.Date.today()
            r.write(update_data)

            if r._should_create_landed_cost():
                cost_lines = self.env['stock.landed.cost.lines']
                valuation_ajustment_lines = self.env['stock.valuation.adjustment.lines']
                if r.tax_line_ids:
                    landed_cost = self.env['stock.landed.cost'].create(r._prepare_landed_cost_data())
                    for line in r.tax_line_ids.filtered(lambda x: not x.is_vat):
                        cost_line = cost_lines.create(line._prepare_landed_cost_line_data(landed_cost))
                        valuation_ajustment_lines.create(line._prepare_landed_cost_adjustment_line_data(cost_line))

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        self.partner_id = self.picking_type_id.custom_authority_id
        if self.picking_type_id and not self.picking_type_id.custom_authority_id:
            return {'warning': {
                'message': _("You may want to specify a partner as Custom Authority for the operation type '%s'"
                             " so that you can save your time in the future.\n"
                             "This can be done by opening the form view of the operation type and specify a partner there")
                             % (self.picking_type_id.name,)
                        }
                    }

    def button_compute_tax_lines(self):
        for r in self:
            if r.state not in ('draft', 'open'):
                raise UserError(_("You cannot do taxes computation for the declaration '%s' which is neither in Draft state or Open state.") % (r.name,))
        self._set_tax_lines()

    def _get_tax_line_model(self):
        raise ValidationError(_("The method `_get_tax_line_model()` has not been implemented for the model `%s`") % (self._name,))

    def _prepare_tax_lines_data(self):
        self.ensure_one()
        taxes_grouped = self.custom_declaration_line_ids.get_taxes_values()
        tax_lines = self.env[self._get_tax_line_model()]
        for tax in taxes_grouped:
            tax_lines += tax_lines.new(tax)
        return tax_lines

    def _set_tax_lines(self):
        for r in self:
            r.tax_line_ids = r._prepare_tax_lines_data()

    def get_unreconcile_tax_aml(self):
        self.ensure_one()
        return self.mapped('account_move_ids.line_ids').filtered(
            lambda l: l.tax_line_id \
            and not l.full_reconcile_id \
            and l.parent_state != 'cancel' \
            and l.partner_id.id == self.partner_id.id \
            and float_compare(abs(l.amount_residual), 0.0, precision_rounding=self.company_id.currency_id.rounding) == 1)

    def _compute_is_paid(self):
        for r in self:
            unreconcile_tax_aml = r.get_unreconcile_tax_aml()
            if float_compare(abs(sum(unreconcile_tax_aml.mapped('amount_residual'))), 0.0, precision_rounding=self.currency_id.rounding) == 1:
                r.is_paid = False
            else:
                r.is_paid = True

    def _get_inconsistent_pickings(self):
        """
        This method support to check consistency between selected picking and declaration
        The check based on product_id, qty and product_uom, then return list of inconsistent pickings
        """
        self.ensure_one()
        return self.stock_picking_ids

    def _prepare_landed_cost_data(self):
        self.ensure_one()
        account_journal_id = self.company_id.landed_cost_journal_id
        if not account_journal_id:
            raise ValidationError(_('There is no account journal defined on the Landed Cost Journal for current company.'))
        return {
                'date': self.clearance_date,
                'picking_ids': [(6, 0, self.stock_picking_ids.ids)],
                'account_journal_id': account_journal_id.id,
            }

    def _should_create_landed_cost(self):
        return False

    def _get_exists_requested_pickings(self):
        self.ensure_one()
        exists_requests = self.search([('state', '!=', 'cancel'), ('id', '!=', self.id)])
        return self.stock_picking_ids & exists_requests.stock_picking_ids
