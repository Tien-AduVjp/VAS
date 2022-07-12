from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import format_date


class CrossoveredBudgetLine(models.Model):
    _name = 'crossovered.budget.line'
    _description = "Budget Line"

    name = fields.Char(compute='_compute_line_name')
    crossovered_budget_id = fields.Many2one('crossovered.budget', 'Budget', ondelete='cascade', index=True, required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    analytic_group_id = fields.Many2one('account.analytic.group', 'Analytic Group', related='analytic_account_id.group_id', readonly=True)
    general_budget_id = fields.Many2one('account.budget.post', string='Budgetary Position',
                                        help="A Budgetary Position is an Odoo document that contains the general accounts for which you want"
                                        " to keep budgets (typically expense or income accounts). They need to be defined so Odoo can know"
                                        " which accounts it needs to go get the budget information.\n"
                                        "For example, we need to define what accounts relates to a project's expenses,"
                                        " just create a new budgetary position and add items of several expense accounts.")
    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)
    paid_date = fields.Date(string='Paid Date', help="Paid Date is used for Theoretical Amount computation. If Paid Date is"
                            " specified later than today, the Theoretical Amount will be zero. If Paid Date is earlier than"
                            " today, the Theoretical Amount will be equal to the Planned Amount. In case no Paid Date is"
                            " specified, the Theoretical Amount will be calculated based on the elapsed time counting from"
                            " the Start Date.")
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    planned_amount = fields.Monetary(
        'Planned Amount', required=True,
        help="Amount you plan to earn/spend. Record a positive amount if it is a revenue and a negative amount if it is a cost.")
    practical_amount = fields.Monetary(compute='_compute_practical_amount', string='Practical Amount',
                                       help="The amount you have actually earned or spent. It is computed automatically based on"
                                       " the related Analytics Items (in analytic accounting) and Journal Items (in general accounting)")
    theoretical_amount = fields.Monetary(compute='_compute_theoretical_amount', string='Theoretical Amount',
                                         help="Amount you are supposed to have earned/spent at this date which will be"
                                         " automatically computed based on Paid Date and the elapsed time counting from"
                                         " the Start Date. If Paid Date is specified later than today, the Amount will be"
                                         " equal to zero. If Paid Date is earlier than today, the Amount will be equal to"
                                         " the Planned Amount. In case no Paid Date is specified, the Theoretical Amount"
                                         " will be calculated based on the elapsed time counting from the Start Date.")
    percentage = fields.Float(compute='_compute_percentage', string='Achievement',
                              help="Comparison between practical and theoretical amount. This measure tells you if you are below or over budget.")
    company_id = fields.Many2one(related='crossovered_budget_id.company_id', comodel_name='res.company', string='Company', store=True, readonly=True)
    is_above_budget = fields.Boolean(compute='_is_above_budget')
    crossovered_budget_state = fields.Selection(related='crossovered_budget_id.state', string='Budget State', store=True, readonly=True)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        # overrides the default read_group in order to compute the computed fields manually for the group

        fields_list = {'practical_amount', 'theoretical_amount', 'percentage'}

        # remove all the aggregate functions of non-stored fields to avoid error on pivot view
        def truncate_aggr(field):
            field_no_aggr = field.split(':', 1)[0]
            if field_no_aggr in fields_list:
                return field_no_aggr
            return field
        fields = {truncate_aggr(field) for field in fields}

        result = super(CrossoveredBudgetLine, self).read_group(
            domain,
            list(fields - fields_list),
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy
            )
        
        if any(x in fields for x in fields_list):
            for group_line in result:

                # initialise fields to compute to 0 if they are requested
                if 'practical_amount' in fields:
                    group_line['practical_amount'] = 0
                if 'theoretical_amount' in fields:
                    group_line['theoretical_amount'] = 0
                if 'percentage' in fields:
                    group_line['percentage'] = 0
                    group_line['practical_amount'] = 0
                    group_line['theoretical_amount'] = 0

                if group_line.get('__domain'):
                    all_budget_lines_that_compose_group = self.search(group_line['__domain'])
                else:
                    all_budget_lines_that_compose_group = self.search([])
                for budget_line_of_group in all_budget_lines_that_compose_group:
                    if 'practical_amount' in fields or 'percentage' in fields:
                        group_line['practical_amount'] += budget_line_of_group.practical_amount

                    if 'theoretical_amount' in fields or 'percentage' in fields:
                        group_line['theoretical_amount'] += budget_line_of_group.theoretical_amount

                    if 'percentage' in fields:
                        if group_line['theoretical_amount']:
                            # use a weighted average
                            group_line['percentage'] = float(
                                (group_line['practical_amount'] or 0.0) / group_line['theoretical_amount'])

        return result

    def _is_above_budget(self):
        for r in self:
            if r.theoretical_amount >= 0:
                r.is_above_budget = r.practical_amount > r.theoretical_amount
            else:
                r.is_above_budget = r.practical_amount < r.theoretical_amount

    @api.depends('crossovered_budget_id', 'general_budget_id', 'analytic_account_id')
    def _compute_line_name(self):
        # just in case someone opens the budget line in form view
        for r in self:
            computed_name = r.crossovered_budget_id.name
            if r.general_budget_id:
                computed_name += ' - ' + r.general_budget_id.name
            if r.analytic_account_id:
                computed_name += ' - ' + r.analytic_account_id.name
            r.name = computed_name

    def _prepare_analytic_lines_domain(self):
        domain = [
            ('account_id', '=', self.analytic_account_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ]
        if self.general_budget_id:
            domain += self.general_budget_id._prepare_analytic_lines_domain()
            if self.crossovered_budget_id.posted_items_only:
                # either without journal item or with posted journal items
                domain += ['|', ('move_id', '=', False), ('move_id.move_id.state', '=', 'posted')]
        return domain

    def _prepare_account_move_lines_domain(self):
        domain = [
            ('account_id', 'in', self.general_budget_id.account_ids.ids),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to)
            ]
        if self.crossovered_budget_id.posted_items_only:
            domain += [('move_id.state', '=', 'posted')]
        return domain

    def _compute_practical_amount(self):
        self.flush()
        for r in self:
            if r.analytic_account_id:
                AccountAnalyticLine = self.env['account.analytic.line']
                where_query = AccountAnalyticLine._where_calc(r._prepare_analytic_lines_domain())
                if not r.env.user.has_group('to_account_budget.group_budget_user') or not r.env.user.has_group('account.group_account_invoice'):
                    AccountAnalyticLine.check_access_rights('read')
                    AccountAnalyticLine._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(account_analytic_line.amount) from " + from_clause + " where " + where_clause

            else:
                AccountMoveLine = self.env['account.move.line']
                where_query = AccountMoveLine._where_calc(r._prepare_account_move_lines_domain())
                if not r.env.user.has_group('to_account_budget.group_budget_user') or not r.env.user.has_group('account.group_account_invoice'):
                    AccountMoveLine.check_access_rights('read')
                    AccountMoveLine._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            r.practical_amount = r.env.cr.fetchone()[0] or 0.0

    def _compute_theoretical_amount(self):
        # beware: 'today' variable is mocked in the python tests and thus, its implementation matter
        today = fields.Date.today()
        for r in self:
            if r.paid_date:
                if today <= r.paid_date:
                    theo_amt = 0.00
                else:
                    theo_amt = r.planned_amount
            else:
                # timedelta must include the start and end date
                line_timedelta = r.date_to - r.date_from + timedelta(days=1)
                elapsed_timedelta = today - r.date_from + timedelta(days=1)

                if elapsed_timedelta.days < 0:
                    # If the budget line has not started yet, theoretical amount should be zero
                    theo_amt = 0.00
                elif line_timedelta.days > 0 and today < r.date_to:
                    # If today is between the budget line date_from and date_to
                    theo_amt = (elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * r.planned_amount
                else:
                    theo_amt = r.planned_amount
            r.theoretical_amount = theo_amt

    def _compute_percentage(self):
        for r in self:
            if not r.currency_id.is_zero(r.theoretical_amount):
                r.percentage = float((r.practical_amount or 0.0) / r.theoretical_amount)
            else:
                r.percentage = 0.00

    @api.constrains('general_budget_id', 'analytic_account_id')
    def _must_have_analytical_or_budgetary_or_both(self):
        for r in self:
            if not r.analytic_account_id and not r.general_budget_id:
                raise ValidationError(
                    _("You have to enter at least either a budgetary position or analytic account on a budget line."))

    def action_open_budget_entries(self):
        self.ensure_one()
        if self.analytic_account_id:
            # if there is an analytic account, then the analytic items are loaded
            action_id = self.env.ref('analytic.account_analytic_line_action_entries')
            domain = self._prepare_analytic_lines_domain()
        else:
            # otherwise the journal entries booked on the accounts of the budgetary postition are opened
            action_id = self.env.ref('account.action_account_moves_all_a')
            domain = self._prepare_account_move_lines_domain()

        action = action_id.read()[0]
        action['domain'] = domain
        return action

    @api.constrains('date_from', 'date_to')
    def _line_dates_between_budget_dates(self):
        for r in self:
            budget_date_from = r.crossovered_budget_id.date_from
            budget_date_to = r.crossovered_budget_id.date_to

            budget_date_from_str = format_date(r.env, budget_date_from)
            budget_date_to_str = format_date(r.env, budget_date_to)

            if r.date_from:
                date_from = r.date_from
                if date_from < budget_date_from or date_from > budget_date_to:
                    raise ValidationError(_("Start Date of the budget line '%s' should be included in the Period (%s ~ %s) of the budget %s")
                                          % (r.display_name, budget_date_from_str, budget_date_to_str, r.crossovered_budget_id.name))

            if r.date_to:
                date_to = r.date_to
                if date_to < budget_date_from or date_to > budget_date_to:
                    raise ValidationError(_("End Date of the budget line '%s' should be included in the Period (%s ~ %s) of the budget %s")
                                          % (r.display_name, budget_date_from_str, budget_date_to_str, r.crossovered_budget_id.name))
