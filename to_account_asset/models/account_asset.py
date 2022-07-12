import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class AccountAssetAsset(models.Model):
    _name = 'account.asset.asset'
    _description = 'Asset/Revenue Recognition'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    entry_count = fields.Integer(compute='_entry_count', string='# Asset Entries')
    posted_entry_count = fields.Integer(compute='_entry_count', help='A technical field to show/hide Set to Draft button.')
    name = fields.Char(string='Asset Name', required=True, readonly=True, states={'draft': [('readonly', False)]})
    code = fields.Char(string='Reference', size=32, readonly=True, states={'draft': [('readonly', False)]})
    value = fields.Float(string='Original Value', required=True, readonly=True, digits=0, states={'draft': [('readonly', False)]})
    original_move_line_ids = fields.Many2many('account.move.line', 'asset_purchase_move_line_rel', 'asset_id', 'move_line_id',
                                              string='Related Purchase Journal Items',
                                              readonly=False, states={
                                                  'open': [('readonly', True)],
                                                  'close': [('readonly', True)],
                                                  'stock_in': [('readonly', True)],
                                                  'sold': [('readonly', True)],
                                                  'disposed': [('readonly', True)],
                                                  },
                                              compute='_get_original_move_lines', inverse='_set_original_move_lines', store=True,
                                              help="The journal items related to purchases of this asset")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env.company)
    note = fields.Text()
    category_id = fields.Many2one('account.asset.category', string='Category', required=True, change_default=True, readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date(string='Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=fields.Date.context_today)
    #TODO: Remove close state in Odoo 14
    state = fields.Selection([
        ('draft', 'Draft'), ('open', 'Running'), ('close', 'Close'),
        ('stock_in', 'Stock-In'), ('sold', 'Sold'), ('disposed', 'Disposed')], 'Status', required=True, copy=False, default='draft',
        help="When an asset is created, the status is 'Draft'.\n"
            "When an asset is confirmed, the status is 'Running'. The depreciation lines is created and can be posted in the accounting.\n"
            "When an asset is sold, the status is 'Sold'. When an asset is disposed, the status is 'Disposed'\n"
            "You can manually close an asset when the depreciation is over. If the last line of depreciation is posted, the asset automatically goes in that status.")
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True, states={'draft': [('readonly', False)]})
    depreciation_expense_account_id = fields.Many2one('account.account', string='Depreciation Entries: Expense Account', 
                                                      readonly=True, states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
                                                      domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
                                                      help="Account used in the periodical entries, to record a part of the asset as expense."
                                                      "When no account is set here, the Depreciation Entries: Expense Account "
                                                       "on Asset Category will be used instead.")
    revaluation_decrease_account_id = fields.Many2one('account.account', string='Revaluation Entries: Decrease Asset Account', 
                                                      readonly=True, states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
                                                      domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
                                                      help="Account used in the revaluation entries, to revaluation decrease a part of the asset. "
                                                      "When no account is set here, the Revaluation Entries: Decrease Asset Account "
                                                       "on Asset Category will be used instead.")
    revaluation_increase_account_id = fields.Many2one('account.account', string='Revaluation Entries: Increase Asset Account', 
                                                      readonly=True, states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
                                                      domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
                                                      help="Account used in the revaluation entries, to revaluation increase a part of the asset. "
                                                      "When no account is set here, the Revaluation Entries: Increase Asset Account "
                                                       "on Asset Category will be used instead.")
    method = fields.Selection([('linear', 'Linear'), ('degressive', 'Degressive'), ('degressive_then_linear', 'Accelerated Degressive')], 
                              string='Computation Method',
                              required=True, readonly=True, states={'draft': [('readonly', False)]},
                              default='linear',
                              help="The method that is used to compute the amount of depreciation lines.\n"
                                   "  * Linear = Original Value / Number of Depreciations\n"
                                   "  * Degressive = Residual Value * Degressive Factor\n"
                                   "  * Accelerated Degressive: Like Degressive but to keep minimum depreciation value equal to Linear value\n")
    method_number = fields.Integer(string='Number of Depreciations', readonly=True, states={'draft': [('readonly', False)]}, default=5, help="Please enter the number of depreciations that is needed to depreciate your asset")
    method_period = fields.Integer(string='Number of Months in a Period', required=True, readonly=True, default=12, states={'draft': [('readonly', False)]},
        help="Choose the time between 2 depreciations here, in months")
    method_end = fields.Date(string='Ending Date', readonly=True, states={'draft': [('readonly', False)]})
    method_progress_factor = fields.Float(string='Degressive Factor', readonly=True, default=0.3, states={'draft': [('readonly', False)]})
    value_residual = fields.Float(compute='_amount_residual', method=True, digits=0, string='Residual Value')
    method_time = fields.Selection([('number', 'Number of Entries'), ('end', 'Ending Date')], string='Time Method', required=True, readonly=True, default='number', states={'draft': [('readonly', False)]},
        help="Choose the method to use to compute the dates and number of entries.\n"
             "  * Number of Entries: Fix the number of entries and the time between 2 depreciations.\n"
             "  * Ending Date: Choose the time between 2 depreciations and the date the depreciations won't go beyond.")
    prorata = fields.Boolean(string='Prorata Temporis', readonly=True, states={'draft': [('readonly', False)]},
        help='Indicates that the first depreciation entry for this asset have to be done from the asset date instead of the first January / Start date of fiscal year')
    depreciation_line_ids = fields.One2many('account.asset.depreciation.line', 'asset_id', string='Depreciation Lines', readonly=True, states={'draft': [('readonly', False)], 'open': [('readonly', False)]})
    revaluation_line_ids = fields.One2many('account.asset.revaluation.line', 'asset_id', string='Revaluation Asset', readonly=True, states={'draft': [('readonly', False)], 'open': [('readonly', False)]})
    depreciation_progress = fields.Float(string='Depreciation Progress', compute='_compute_depreciation_progress', store=True)
    salvage_value = fields.Float(string='Non-Depreciated Value', digits=0, readonly=True, states={'draft': [('readonly', False)]},
        help="It is the amount you plan to have that you cannot depreciate.")
    revaluation_value = fields.Float(string='Revaluation Value', compute='_amount_residual', digits=0, readonly=True, help="It is the amount you plan to have that you cannot depreciate.", tracking=True, copy=False)
    invoice_line_id = fields.Many2one('account.move.line', string='Invoice Line', tracking=True, copy=False, readonly=True, states={'draft': [('readonly', False)]})
    invoice_id = fields.Many2one('account.move', string='Invoice', related='invoice_line_id.move_id', store=True, copy=False)
    move_ids = fields.One2many('account.move', 'account_asset_id', string='Journal Entries', readonly=True, 
                               help='This technical field that stores all the journal disposal entries, journal sell entries')
    type = fields.Selection(related="category_id.type", string='Type', required=True, readonly=False)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', groups='analytic.group_analytic_accounting')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tag', groups='analytic.group_analytic_tags')
    product_id = fields.Many2one('product.product', string='Asset Product', help="The product that presents the asset", readonly=True, states={'draft': [('readonly', False)]})
    date_first_depreciation = fields.Selection([
        ('last_day_period', 'Based on Last Day of Month'),
        ('manual', 'Manual')],
        string='Depreciation Dates', default='manual',
        readonly=True, states={'draft': [('readonly', False)]}, required=True,
        help='The way to compute the date of the first depreciation.\n'
             '  * Based on last day of month: The depreciation dates will be based on the last day of the month.\n'
             '  * Manual: You will need set manually depreciation dates.')
    first_depreciation_date = fields.Date(
        string='First Depreciation Date',
        readonly=True, states={'draft': [('readonly', False)]},
        help='It simply changes its accounting date. This date does not alter the computation of the first journal entry in case of prorata temporis assets.'
    )

    @api.constrains('date_first_depreciation', 'first_depreciation_date', 'date')
    def _check_first_depreciation_date(self):
        for r in self.filtered(lambda r: r.date_first_depreciation == 'manual'):
            if r.first_depreciation_date < r.date:
                raise ValidationError(_("The first depreciation date of asset '%s' cannot be set before the date!") % r.name)

    def copy_data(self, default=None):
        if default is None:
            default = {}
        default.update({
            'name': _('%s (copy)') % self.name,
            'original_move_line_ids': [(6, 0, self.original_move_line_ids.ids)],
            'analytic_account_id': self.sudo().analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.sudo().analytic_tag_ids.ids)],
            })
        return super(AccountAssetAsset, self).copy_data(default)

    def unlink(self):
        for asset in self:
            if asset.state != 'draft':
                state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}
                raise UserError(_('You cannot delete a document that is in %s state.') % state_description_values.get(asset.state))
            for depreciation_line in asset.depreciation_line_ids:
                if depreciation_line.move_id and (depreciation_line.move_id.state == 'posted' or (depreciation_line.move_id.name != '/' and not self.env.context.get('force_delete', False))):
                    raise UserError(_('You cannot delete a document that contains posted entries.'))
        return super(AccountAssetAsset, self).unlink()

    @api.model
    def _cron_generate_entries(self):
        self.compute_generated_entries(datetime.today())

    @api.model
    def compute_generated_entries(self, date, asset_type=None):
        # Entries generated : one by grouped category and one by asset from ungrouped category
        created_move_ids = []
        type_domain = []
        if asset_type:
            type_domain = [('type', '=', asset_type)]

        ungrouped_assets = self.env['account.asset.asset'].search(type_domain + [('state', '=', 'open'), ('category_id.group_entries', '=', False)])
        created_move_ids += ungrouped_assets._compute_entries(date, group_entries=False)

        for grouped_category in self.env['account.asset.category'].search(type_domain + [('group_entries', '=', True)]):
            assets = self.env['account.asset.asset'].search([('state', '=', 'open'), ('category_id', '=', grouped_category.id)])
            created_move_ids += assets._compute_entries(date, group_entries=True)
        return created_move_ids

    @api.depends('invoice_line_id')
    def _get_original_move_lines(self):
        for r in self:
            if not r.invoice_line_id:
                r.original_move_line_ids = [(3, line) for line in r.original_move_line_ids]
            else:
                if r._context.get('do_not_recompute_original_move_lines'):
                    r.original_move_line_ids = [(6, 0, r.original_move_line_ids.ids)]
                else:
                    r.original_move_line_ids = [(6, 0, [r.invoice_line_id.id])]

    def _set_original_move_lines(self):
        for r in self.with_context(do_not_recompute_original_move_lines=True):
            invoice_lines = r.original_move_line_ids.filtered(lambda l: l.move_id.type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund'))
            if invoice_lines:
                r.invoice_line_id = invoice_lines[0].id
            else:
                r.invoice_line_id = False

    @api.onchange('original_move_line_ids')
    def _onchange_original_move_line_ids(self):
        self.value = sum(self.original_move_line_ids.mapped('balance')) if self.original_move_line_ids else 0.0

    @api.depends('value', 'salvage_value', 'value_residual', 'revaluation_value')
    def _compute_depreciation_progress(self):
        for r in self:
            total = r.value - r.salvage_value + r.revaluation_value
            if r.currency_id.is_zero(total):
                r.depreciation_progress = 100.0
            else:
                r.depreciation_progress = 100.0 - 100.0 * r.value_residual / total

    def _compute_board_amount(self, sequence, residual_amount, amount_to_depr, undone_dotation_number, depreciation_line_count, total_days):
        def _degressive_prorata_amount(residual_amount):
            prorata_date = self.date
            if int(self.method_period) % 12 != 0:
                month_days = calendar.monthrange(prorata_date.year, prorata_date.month)[1]
                days = month_days - prorata_date.day + 1
                amount = (residual_amount * self.method_progress_factor) / month_days * days
            else:
                days = (self.asset_id.company_id.compute_fiscalyear_dates(prorata_date)['date_to'] - prorata_date).days + 1
                amount = (residual_amount * self.method_progress_factor) / total_days * days
            return amount
        
        amount = 0
        if sequence == undone_dotation_number:
            amount = residual_amount
        else:
            if self.method == 'linear':
                amount = amount_to_depr / (undone_dotation_number - depreciation_line_count)
                if self.prorata:
                    date = self.date
                    year, month, day = date.year, date.month, date.day
                    if depreciation_line_count == 0:
                        amount = amount_to_depr / self.method_number
                    else:
                        month_days = calendar.monthrange(year, month)[1]
                        month = (day - 1) / month_days
                        amount = amount_to_depr / (self.method_number - depreciation_line_count + month)
                    if sequence == 1:
                        if self.method_period % 12 != 0:
                            start_date = self.date.replace(day=1)
                            date = self.date + relativedelta(months=self.method_period - 1)
                            end_date = date.replace(day=calendar.monthrange(date.year, date.month)[1])

                            month_days = (end_date - start_date).days + 1
                            days = month_days - day + 1
                            amount = (amount_to_depr / self.method_number) / month_days * days
                        else:
                            days = (self.company_id.compute_fiscalyear_dates(date)['date_to'] - date).days + 1
                            amount = (amount_to_depr / self.method_number) / total_days * days
            elif self.method == 'degressive':
                amount = residual_amount * self.method_progress_factor
                if self.prorata:
                    if sequence == 1:
                        amount = _degressive_prorata_amount(residual_amount)
            elif self.method == 'degressive_then_linear':
                amount = residual_amount * self.method_progress_factor
                if self.prorata:
                    if sequence == 1:
                        amount = _degressive_prorata_amount(residual_amount)
                linear_amount = self.value_residual / self.method_number
                if float_compare(amount, linear_amount, precision_rounding=self.currency_id.rounding) == -1:
                    if float_compare(linear_amount, residual_amount, precision_rounding=self.currency_id.rounding) <= 0:
                        amount = linear_amount
                    else:
                        amount = residual_amount
        return amount

    def _compute_board_undone_dotation_nb(self, depreciation_date):
        undone_dotation_number = self.method_number
        if self.method_time == 'end':
            end_date = self.method_end
            undone_dotation_number = 0
            while depreciation_date <= end_date:
                depreciation_date = date(depreciation_date.year, depreciation_date.month, depreciation_date.day) + relativedelta(months=+self.method_period)
                undone_dotation_number += 1
        if self.prorata and self.date.day != 1:
            undone_dotation_number += 1
        return undone_dotation_number

    def _compute_depreciation_board(self):
        self.ensure_one()
        posted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: x.move_check and x.move_id.state == 'posted').sorted(key=lambda l: l.depreciation_date)
        unposted_depreciation_line_ids = self.depreciation_line_ids - posted_depreciation_line_ids
        last_posted_depreciation_date = posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date or False
        if last_posted_depreciation_date:
            unposted_depreciation_line_ids = unposted_depreciation_line_ids.filtered(lambda x: x.depreciation_date > last_posted_depreciation_date)
        revaluation_line_ids = self.revaluation_line_ids.filtered(lambda line: line.move_check and line.move_id.state == 'posted').sorted(key='revaluation_date')
        # remove all move that have been linked to depreciation lines in posted state, then not in unposted state
        unposted_depreciation_line_ids.filtered(lambda x: x.move_check and x.move_id.name != '/').write({'move_id': False})
        # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
        commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

        if self.value_residual != 0.0:
            value = self.value
            amount_to_depr = residual_amount = self.value_residual - self.revaluation_value

            # if we already have some previous validated entries, starting date is last entry + method period
            if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
                last_depreciation_date = posted_depreciation_line_ids[-1].depreciation_date
                depreciation_date = last_depreciation_date + relativedelta(months=+self.method_period)
                if self.date_first_depreciation == 'last_day_period':
                    depreciation_date = depreciation_date.replace(day=calendar.monthrange(depreciation_date.year, depreciation_date.month)[1])
            else:
                # depreciation_date computed from the date
                depreciation_date = self.date
                if self.date_first_depreciation == 'last_day_period':
                    # depreciation_date = the last day of the month
                    depreciation_date = depreciation_date + relativedelta(day=31)
                    # ... or fiscalyear depending the number of period
                    if self.method_period == 12:
                        depreciation_date = depreciation_date + relativedelta(month=int(self.company_id.fiscalyear_last_month))
                        depreciation_date = depreciation_date + relativedelta(day=self.company_id.fiscalyear_last_day)
                        if depreciation_date < self.date:
                            depreciation_date = depreciation_date + relativedelta(years=1)
                elif self.first_depreciation_date and self.first_depreciation_date != self.date:
                    # depreciation_date set manually from the 'first_depreciation_date' field
                    depreciation_date = self.first_depreciation_date

            total_days = (depreciation_date.year % 4) and 365 or 366
            month_day = depreciation_date.day
            undone_dotation_number = self._compute_board_undone_dotation_nb(depreciation_date)
            
            depreciation_line_count = len(posted_depreciation_line_ids)
            
            for x in range(depreciation_line_count, undone_dotation_number):
                sequence = x + 1
                
                this_depreciation_date = depreciation_date
                depreciation_date = depreciation_date + relativedelta(months=+self.method_period)

                if month_day > 28 and self.date_first_depreciation == 'manual':
                    max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(day=min(max_day_in_month, month_day))

                # datetime doesn't take into account that the number of days is not the same for each month
                if self.date_first_depreciation == 'last_day_period':
                    max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(day=max_day_in_month)
                    if self.prorata and self.date.day != 1 and sequence == undone_dotation_number - 1:
                        depreciation_date = depreciation_date.replace(day=(self.date.day - 1))
                
                for revl in revaluation_line_ids:
                    if (posted_depreciation_line_ids and posted_depreciation_line_ids[0].depreciation_date <= revl.revaluation_date <= this_depreciation_date) \
                       or (this_depreciation_date <= revl.revaluation_date < depreciation_date):
                        revl_value = revl.value if revl.method == 'increase' else -revl.value
                        revaluation_line_ids -= revl
                        residual_amount += revl_value
                        amount_to_depr = residual_amount
                        value += revl_value
                        depreciation_line_count = x
                
                amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr, undone_dotation_number, depreciation_line_count, total_days)
                amount = self.currency_id.round(amount)
                if self.currency_id.is_zero(amount):
                    continue
                residual_amount -= amount
                
                vals = {
                    'amount': amount,
                    'asset_id': self.id,
                    'method_period': self.method_period,
                    'sequence': sequence,
                    'name': (self.code or '') + '/' + str(sequence),
                    'remaining_value': residual_amount,
                    'depreciated_value': value - (self.salvage_value + residual_amount),
                    'depreciation_date': this_depreciation_date,
                }
                
                commands.append((0, False, vals))
        
        if revaluation_line_ids:
            raise UserError(_('Date of revaluation is not valid, because it is outside the depreciation period!'))
        
        self.write({'depreciation_line_ids': commands})

        return True

    def validate(self):
        self.write({'state': 'open'})
        fields = [
            'method',
            'method_number',
            'method_period',
            'method_end',
            'method_progress_factor',
            'method_time',
            'salvage_value',
            'invoice_id',
        ]
        ref_tracked_fields = self.env['account.asset.asset'].fields_get(fields)
        for asset in self:
            tracked_fields = ref_tracked_fields.copy()
            if asset.method == 'linear':
                del(tracked_fields['method_progress_factor'])
            if asset.method_time != 'end':
                del(tracked_fields['method_end'])
            else:
                del(tracked_fields['method_number'])
            dummy, tracking_value_ids = asset._message_track(tracked_fields, dict.fromkeys(fields))
            asset.message_post(subject=_('Asset created'), tracking_value_ids=tracking_value_ids)

    def _return_disposal_view(self, move_ids):
        name = _('Disposal Move')
        view_mode = 'form'
        if len(move_ids) > 1:
            name = _('Disposal Moves')
            view_mode = 'tree,form'
        return {
            'name': name,
            'view_mode': view_mode,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': move_ids[0],
        }

    def _unlink_all_unposted_depreciation_lines(self):
        """
        This method unlinks all unlisted depreciation lines, 
        and also updates the values of Number of Depreciations as sum of all posted depreciation lines, Ending Date 
        as the stock-in's manual date/ today.
        Final, when stock-in/selling/disposaling, create a new depreciation line with amount 
        of the depreciated dates that are not posted.
        """
        date = self._context.get('stock_in_date', False)
        if date:
            date = fields.Date.context_today(self, date)
        elif self._context.get('disposed_date', False):
            date = self._context.get('disposed_date', False)
        else:
            date = self._context.get('stopped_depreciating_date', fields.Date.today())

        for r in self:
            sequence = False
            depreciation_period = 0
            if r.depreciation_line_ids:
                start_date, end_date = r._calculate_data_of_depreciation_line(date)
                depreciation_period = (end_date - start_date).days

            number_of_days_in_a_period = (depreciation_period + 1) or (r.method_period * 30)

            posted_depreciation_line_ids = r.depreciation_line_ids.filtered(lambda x: x.move_check and x.move_id.state == 'posted')
            last_posted_depreciation_line = False
            if posted_depreciation_line_ids:

                last_posted_depreciation_line = posted_depreciation_line_ids \
                                                    .filtered(lambda l: start_date <= l.depreciation_date <= end_date) \
                                                    .sorted(key='depreciation_date')[-1:]
                if posted_depreciation_line_ids and date < posted_depreciation_line_ids[-1].depreciation_date:
                    raise UserError(_("You cannot perform this action on the asset '%s' that contains posted depreciation lines before %s date.") % (r.name, date))

            first_unposted_depreciation_line = False
            amount = 0
            unposted_depreciation_line_ids = r.depreciation_line_ids - posted_depreciation_line_ids
            if unposted_depreciation_line_ids:
                first_unposted_depreciation_line = unposted_depreciation_line_ids.sorted(key='depreciation_date')[0]
                if date > first_unposted_depreciation_line.depreciation_date:
                    raise UserError(_("You have not posted all depreciation lines on the asset '%s' before %s date.") % (r.name, date))

                if date == first_unposted_depreciation_line.depreciation_date:
                    amount = first_unposted_depreciation_line.amount * (date - start_date).days / number_of_days_in_a_period
                elif last_posted_depreciation_line and date <= end_date:
                    amount = last_posted_depreciation_line.amount * ((date - end_date).days - 1) / number_of_days_in_a_period
                else:
                    amount = first_unposted_depreciation_line.amount * (date - start_date).days / number_of_days_in_a_period
            elif last_posted_depreciation_line and date <= end_date:
                first_unposted_depreciation_line = last_posted_depreciation_line.copy()
                amount = last_posted_depreciation_line.amount * ((date - end_date).days - 1) / number_of_days_in_a_period
                first_unposted_depreciation_line.update({
                    'sequence': last_posted_depreciation_line.sequence + 1,
                    'move_id': False,
                    })

            if not r.currency_id.is_zero(amount):
                amount = r.currency_id.round(amount)
                first_unposted_depreciation_line.write({
                    'amount': amount,
                    'depreciation_date': date,
                    'depreciated_value': posted_depreciation_line_ids \
                        and amount + posted_depreciation_line_ids[-1].depreciated_value \
                        or amount,
                    'remaining_value': r.value_residual - amount,
                    })

                unposted_depreciation_line_ids -= first_unposted_depreciation_line

            old_values = {
                'method_end': r.method_end,
                'method_number': r.method_number,
            }

            # Remove all unposted depr. lines
            commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

            # Create a new depr. line with the residual amount and post it
            sequence = len(r.depreciation_line_ids) - len(unposted_depreciation_line_ids)
            r.with_context(force_delete=True).write({'depreciation_line_ids': commands, 'method_end': date, 'method_number': sequence})
            tracked_fields = self.env['account.asset.asset'].fields_get(['method_number', 'method_end'])
            changes, tracking_value_ids = r._message_track(tracked_fields, old_values)
            if changes:

                r.message_post(subject=_('Asset sold or disposed. Accounting entry awaiting for validation.'), tracking_value_ids=tracking_value_ids)

            # Create a new depr. line with amount of days past and post it
            if first_unposted_depreciation_line and first_unposted_depreciation_line not in unposted_depreciation_line_ids:
                if first_unposted_depreciation_line.move_id:
                    first_unposted_depreciation_line.move_id.with_context(force_delete=True, do_not_recompute_depreciation_line=True).unlink()

                first_unposted_depreciation_line.create_move(post_move=True)

    def _calculate_data_of_depreciation_line(self, stopped_date):
        """This method to calculate start date and end date of last depreciation line"""
        self.ensure_one()
        tracking_values = self.message_ids.sudo().mapped('tracking_value_ids').filtered(lambda t: 'method_period' in t.field)
        start_date = end_date = False
        first_method_period = False
        for i in range(len(self.depreciation_line_ids)):
            if self.depreciation_line_ids[i].method_period:
                method_period = self.depreciation_line_ids[i].method_period
            else:
                tracks = tracking_values.filtered(lambda t: t.create_date <= self.depreciation_line_ids[i].create_date)
                if tracks:
                    method_period = tracks.sorted(key='create_date')[-1].new_value_integer
                else:
                    method_period = self.method_period

            if i == 0:
                if self.prorata:
                    start_date = self.date
                    first_method_period = method_period
                    if method_period % 12 != 0:
                        date = self.date + relativedelta(months=method_period - 1)
                        end_date = date.replace(day=calendar.monthrange(date.year, date.month)[1])
                    else:
                        end_date = self.company_id.compute_fiscalyear_dates(start_date)['date_to']
                else:
                    if self.date_first_depreciation == 'manual':
                        start_date = self.first_depreciation_date
                    else:
                        start_date = self.date.replace(day=calendar.monthrange(self.date.year, self.date.month)[1])
                    end_date = start_date + relativedelta(days=-1, months=method_period)
            else:
                start_date = end_date + relativedelta(days=1)
                end_date = end_date + relativedelta(months=method_period)
                if self.prorata or self.date_first_depreciation == 'last_day_period':
                    end_date = end_date.replace(day=calendar.monthrange(end_date.year, end_date.month)[1])

            if start_date <= stopped_date <= end_date:
                break

        if self.prorata and all(line.move_id and line.move_id.state == 'posted' for line in self.depreciation_line_ids):
            end_date = start_date + relativedelta(months=first_method_period - 1)
            if first_method_period % 12 != 0:
                end_date = end_date.replace(day=(self.date.day - 1))
            else:
                end_date = end_date.replace(month=self.date.month, day=(self.date.day - 1))

        return start_date, end_date

    def _get_accounting_data_for_asset(self):
        """ Return the accounts to use to post disposal Journal Entries or stock-in Journal Entries"""
        self.ensure_one()
        return {
            'asset_account_id': self.category_id.asset_account_id.id,
            'depreciation_account_id': self.category_id.depreciation_account_id.id, 
            'disposal_account_id': self.category_id.disposal_expense_account_id.id or self.depreciation_expense_account_id.id or self.category_id.depreciation_expense_account_id.id, 
            }

    def _prepare_account_move_vals(self, date):
        self.ensure_one()
        
        category_id = self.category_id
        analytic_account_id = self.sudo().analytic_account_id
        analytic_tag_ids = self.sudo().analytic_tag_ids
        company_currency = self.company_id.currency_id
        current_currency = self.currency_id
        diff_currency = company_currency != current_currency
        prec = company_currency.decimal_places

        total_amount = sum(self.depreciation_line_ids.filtered(lambda line: line.move_check and line.move_id.state != 'cancel').mapped('amount'))
        revaluation_value = sum(self.revaluation_line_ids.filtered(lambda line: line.move_check and line.move_id.state != 'cancel') \
                                                          .mapped(lambda line: line.value if line.method == 'increase' else -line.value))
        value_residual = self.value - total_amount - self.salvage_value + revaluation_value
        
        gross_amount_currency = self.value + revaluation_value
        gross_amount = current_currency._convert(gross_amount_currency, company_currency, self.company_id, date)
        asset_name = self.name
        
        accounts = self._get_accounting_data_for_asset()
        
        move_line_vals = [(0, 0, {'name': asset_name, 
                                 'account_id': accounts['asset_account_id'],
                                 'credit': gross_amount if float_compare(gross_amount, 0.0, precision_digits=prec) > 0 else 0.0,
                                 'debit': 0.0 if float_compare(gross_amount, 0.0, precision_digits=prec) > 0 else -gross_amount,
                                 'partner_id': self.partner_id.id,
                                 'analytic_account_id': analytic_account_id.id if category_id.type == 'sale' else False,
                                 'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
                                 'currency_id': diff_currency and current_currency.id or False,
                                 'amount_currency': diff_currency and -1.0 * gross_amount_currency or 0.0,
                                 })]
        
        depreciation_amount_currency = self.value - value_residual + revaluation_value
        depreciation_amount = current_currency._convert(depreciation_amount_currency, company_currency, self.company_id, date)
        if float_compare(depreciation_amount, 0.0, precision_digits=prec) > 0:
            move_line_vals.append((0, 0, {'name': asset_name, 
                                'account_id': accounts['depreciation_account_id'], 
                                'debit': depreciation_amount if float_compare(depreciation_amount, 0.0, precision_digits=prec) > 0 else 0.0, 
                                'credit': 0.0 if float_compare(depreciation_amount, 0.0, precision_digits=prec) > 0 else -depreciation_amount,
                                'partner_id': self.partner_id.id,
                                'analytic_account_id': analytic_account_id.id if category_id.type == 'purchase' else False,
                                'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
                                'currency_id': diff_currency and current_currency.id or False,
                                'amount_currency': diff_currency and depreciation_amount_currency or 0.0,
                                         }))
        
        residual_amount_currency = value_residual
        if float_compare(residual_amount_currency, 0.0, precision_digits=prec) > 0:
            residual_amount = current_currency._convert(residual_amount_currency, company_currency, self.company_id, date)
            move_line_vals.append((0, 0, {'name': asset_name, 
                                         'account_id': accounts['disposal_account_id'], 
                                         'debit': residual_amount if float_compare(residual_amount, 0.0, precision_digits=prec) > 0 else 0.0, 
                                         'credit': 0.0 if float_compare(residual_amount, 0.0, precision_digits=prec) > 0 else -residual_amount,
                                         'partner_id': self.partner_id.id,
                                         'analytic_account_id': analytic_account_id.id if category_id.type == 'purchase' else False,
                                         'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
                                         'currency_id': diff_currency and current_currency.id or False,
                                         'amount_currency': diff_currency and residual_amount_currency or 0.0,
                                         }))
        
        move_val = {
            'ref': self.code, 
            'date': date,
            'journal_id': category_id.journal_id.id,
            'line_ids': move_line_vals,
            'account_asset_id': self.id,
            }
        
        return move_val
    
    def create_account_move(self, post_move=True):
        """This method creates a journal disposal entries: D214,811/C211"""
        self.ensure_one()
        account_move_obj = self.env['account.move']
        
        date = self._context.get('stock_in_date', False)
        if date:
            date = fields.Date.context_today(self, date)
        elif self._context.get('disposed_date', False):
            date = self._context.get('disposed_date', False)
        else:
            date = self._context.get('stopped_depreciating_date', fields.Date.today())
        
        depreciation_line_ids = self.depreciation_line_ids.filtered(lambda line: line.move_id.state == 'draft' \
                                                                    and line.depreciation_date != date)
        if depreciation_line_ids:
            raise UserError(_('This depreciation is already linked to a journal entry. Please post or delete it.'))
        
        revaluation_line_ids = self.revaluation_line_ids.filtered(lambda line: line.move_id.state == 'draft')
        if revaluation_line_ids:
            raise UserError(_('This revaluation is already linked to a journal entry. Please post or delete it.'))
            
        move = account_move_obj.create(self._prepare_account_move_vals(date))
        account_move_obj |= move
        self.message_post(body=_("Document closed."))
        asset_val = {
            'move_ids': [(6, 0, account_move_obj.ids)],
            }
        
        if self._context.get('stock_in', False):
            asset_val.update({'state': 'stock_in'})
        elif self._context.get('sell', False):
            asset_val.update({'state': 'sold'})
        elif self._context.get('dispose', False):
            asset_val.update({'state': 'disposed'})
        else:
            asset_val.update({'state': 'close'})
            
        self.write(asset_val)
            # set depreciation last line's value as disposal
        if self.depreciation_line_ids:
            self.depreciation_line_ids.sorted(key='depreciation_date')[-1].write({
                'disposal': True,
                })
        
        if post_move and account_move_obj:
            account_move_obj.filtered(lambda m: any(m.asset_depreciation_ids.mapped('asset_id.category_id.open_asset'))).post()
        return account_move_obj

    def action_compute_depreciation_board(self):
        self._compute_depreciation_board()

    def button_sell(self):
        self.ensure_one()
        self.with_context(sell=True).button_dispose()
        return self.action_view_sales_invoice()
    
    def button_dispose(self):
        self.ensure_one()
        self._unlink_all_unposted_depreciation_lines()
        self.create_account_move(post_move=False)
        return self.open_entries()

    def set_to_draft(self):
        self.write({'state': 'draft'})

    @api.depends('value', 'salvage_value', 'revaluation_line_ids.move_check', 'revaluation_line_ids.value', 'revaluation_line_ids.move_id.state', 
                 'depreciation_line_ids.move_check', 'depreciation_line_ids.amount', 'depreciation_line_ids.move_id.state')
    def _amount_residual(self):
        for r in self:
            total_amount = sum(r.depreciation_line_ids.filtered(lambda line: line.move_check and line.move_id.state == 'posted').mapped('amount'))
            total_revl_amount = sum(r.revaluation_line_ids.filtered(lambda line: line.move_check and line.move_id.state == 'posted') \
                                                          .mapped(lambda line: line.value if line.method == 'increase' else -line.value))
            r.revaluation_value = total_revl_amount
            r.value_residual = r.value - total_amount - r.salvage_value + r.revaluation_value

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.currency_id = self.company_id.currency_id.id

    @api.onchange('date_first_depreciation')
    def onchange_date_first_depreciation(self):
        if self.date_first_depreciation == 'manual':
            self.first_depreciation_date = self._origin.first_depreciation_date or self.date
        else:
            self.first_depreciation_date = False

    @api.depends('depreciation_line_ids.move_id', 'revaluation_line_ids.move_id')
    def _entry_count(self):
        for r in self:
            r.entry_count = len(
                                r.depreciation_line_ids.move_id \
                                | r.move_ids.filtered(lambda move: move.type != 'out_invoice') \
                                | r.revaluation_line_ids.move_id
                            ) or 0
            r.posted_entry_count = len(
                                        (r.depreciation_line_ids.move_id | 
                                         r.move_ids.filtered(lambda move: move.type != 'out_invoice') |
                                         r.revaluation_line_ids.move_id
                                        ).filtered(lambda m: m.state == 'posted' or (m.state == 'draft' and m.name != '/'))
                                    ) or 0

    @api.constrains('prorata', 'method_time')
    def _check_prorata(self):
        for r in self:
            if r.prorata and r.method_time != 'number':
                raise ValidationError(_('Prorata temporis can be applied only for the "number of depreciations" time method.'))

    @api.onchange('category_id')
    def onchange_category_id(self):
        vals = self.onchange_category_id_values(self.category_id.id)
        # We cannot use 'write' on an object that doesn't exist yet
        if vals:
            for k, v in vals['value'].items():
                setattr(self, k, v)

    def onchange_category_id_values(self, category_id):
        if category_id:
            category = self.env['account.asset.category'].browse(category_id)
            return {
                'value': {
                    'method': category.method,
                    'method_number': category.method_number,
                    'method_time': category.method_time,
                    'method_period': category.method_period,
                    'method_progress_factor': category.method_progress_factor,
                    'method_end': category.method_end,
                    'prorata': category.prorata,
                    'date_first_depreciation': category.date_first_depreciation,
                    'analytic_account_id': category.sudo().analytic_account_id.id,
                    'analytic_tag_ids': [(6, 0, category.sudo().analytic_tag_ids.ids)],
                    'depreciation_expense_account_id': category.depreciation_expense_account_id.id,
                    'revaluation_decrease_account_id': category.revaluation_decrease_account_id.id,
                    'revaluation_increase_account_id': category.revaluation_increase_account_id.id,
                    }
                }

    @api.onchange('method_time')
    def onchange_method_time(self):
        if self.method_time != 'number':
            self.prorata = False

    def action_view_sales_invoice(self):
        self.ensure_one()
        move_ids = self.mapped('move_ids').filtered(lambda move: move.type == 'out_invoice')

        # choose the view_mode accordingly
        if len(move_ids) <= 1:
            ctx = dict(self._context or {})
            journal_id = self.env['account.journal']\
                .search([('company_id', '=', self.env.company.id), ('type', '=', 'sale')], limit=1)
            
            dates = self.move_ids.mapped('date')
            date = dates and max(dates) or fields.Date.today()
            ctx.update({
                'default_partner_id': self.env.ref('base.main_partner').id,
                'default_date': date,
                'default_journal_id': journal_id.id,
                'default_type': 'out_invoice',
                'default_journal_type': 'sale',
                'default_account_asset_id': self.id,
                 'default_line_ids': [(0, 0, {
                        'account_id': self.revaluation_increase_account_id.id or self.category_id.revaluation_increase_account_id.id,
                        'quantity': 1.0,
                        'price_unit': 0,
                        })],
                })
            if self.product_id:
                ctx['default_line_ids'][0][2].update({
                        'product_id': self.product_id.id,
                        'name': self.product_id.name,
                        'account_id': self.product_id.product_tmpl_id._get_product_accounts()['income'].id,
                    })
            return {
                'name': _('Create invoice if you are selling the asset'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_id': self.env.ref('account.view_move_form').id,
                'view_mode': 'form',
                'target': 'current',
                'res_id': move_ids.id or False,
                'context': ctx,
                }
        
        action = self.env.ref('account.view_invoice_tree')
        result = action.read()[0]
        result['domain'] = [('account_asset_id', 'in', self.ids)]
        return result

    def _compute_entries(self, date, group_entries=False):
        depreciation_ids = self.env['account.asset.depreciation.line'].search([
            ('asset_id', 'in', self.ids), ('depreciation_date', '<=', date),
            ('move_check', '=', False)])
        if group_entries:
            return depreciation_ids.create_grouped_move()
        return depreciation_ids.create_move()

    @api.model_create_multi
    def create(self, vals_list):
        assets = super(AccountAssetAsset, self.with_context(mail_create_nolog=True)).create(vals_list)
        for asset in assets:
            asset.sudo()._compute_depreciation_board()
        return assets

    def write(self, vals):
        res = super(AccountAssetAsset, self).write(vals)
        if 'depreciation_line_ids' not in vals and 'state' not in vals:
            for rec in self:
                rec._compute_depreciation_board()
        return res

    def open_entries(self):
        moves = self.mapped('depreciation_line_ids.move_id') | self.mapped('move_ids').filtered(lambda move: move.type != 'out_invoice') | self.mapped('revaluation_line_ids.move_id')
        return {
            'name': _('Journal Entries'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', moves.ids)],
        }
