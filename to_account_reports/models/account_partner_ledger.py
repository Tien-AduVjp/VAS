from odoo import models, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, float_is_zero
from datetime import datetime, timedelta
from odoo.osv import expression


class ReportPartnerLedger(models.AbstractModel):
    _inherit = "account.report"
    _name = "account.partner.ledger"
    _description = "Partner Ledger"

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_year'}
    filter_all_entries = False
    filter_unfold_all = False
    filter_account_type = [{'id': 'receivable', 'name': _('Receivable'), 'selected': False}, {'id': 'payable', 'name': _('Payable'), 'selected': False}]
    filter_unreconciled = False
    # TODO add support for partner_id
    filter_account_all = True
    filter_partner_all = True

    def get_templates(self):
        templates = super(ReportPartnerLedger, self).get_templates()
        templates['line_template'] = 'to_account_reports.line_template_partner_ledger_report'
        templates['main_template'] = 'to_account_reports.template_partner_ledger_report'
        return templates

    def get_account_domains(self):
        domain = super(ReportPartnerLedger, self).get_account_domains()
        domain = expression.AND([domain, [('user_type_id.type', 'in', ('payable', 'receivable'))]])
        return domain
    
    def _get_super_columns(self, options):
        columns = [{'string': '', 'merge': 1}]
        columns += [{'string': _('JRNL'), 'merge': 1}]
        columns += [{'string': _('Account'), 'merge': 1}]
        columns += [{'string': _('Countered Accounts'), 'merge': 1}]
        columns += [{'string': _('Ref'), 'merge': 1}]
        columns += [{'string': _('Matching Number'), 'merge': 1}]
        columns += [{'string': _('Opening Balance'), 'merge': 2}]
        columns += [{'string': _('Arising Amount'), 'merge': 2}]
        columns += [{'string': _('Closing Balance'), 'merge': 2}]
    
        return {'columns': columns, 'x_offset': 0, 'merge': 1}
    
    def get_columns_name(self, options):
        columns = [
            {'name': ''},
            {'name': ''},
            {'name': ''},
            {'name': ''},
            {'name': ''},
            {'name': ''},
            {'name': _('Debit'), 'class': 'number text-center'},
            {'name': _('Credit'), 'class': 'number text-center'},
            {'name': _('Debit'), 'class': 'number text-center'},
            {'name': _('Credit'), 'class': 'number text-center'},
            {'name': _('Debit'), 'class': 'number text-center'},
            {'name': _('Credit'), 'class': 'number text-center'},
        ]
        return columns
    
    def do_query(self, options, line_id):
        account_types = [a.get('id') for a in options.get('account_type') if a.get('selected', False)]
        if not account_types:
            account_types = [a.get('id') for a in options.get('account_type')]
        select = ',COALESCE(SUM(\"account_move_line\".debit-\"account_move_line\".credit), 0),SUM(\"account_move_line\".debit),SUM(\"account_move_line\".credit)'
        sql = "SELECT \"account_move_line\".partner_id%s FROM %s WHERE %s%s AND \"account_move_line\".partner_id IS NOT NULL GROUP BY \"account_move_line\".partner_id"
        tables, where_clause, where_params = self.env['account.move.line']._query_get([('account_id.internal_type', 'in', account_types)])
        line_clause = line_id and ' AND \"account_move_line\".partner_id = ' + str(line_id) or ''
        if options.get('unreconciled'):
            line_clause += ' AND \"account_move_line\".full_reconcile_id IS NULL'
        query = sql % (select, tables, where_clause, line_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        results = dict([(k[0], {'balance': k[1], 'debit': k[2], 'credit': k[3]}) for k in results])
        return results

    def group_by_partner_id(self, options, line_id):
        partners = {}
        account_types = [a.get('id') for a in options.get('account_type') if a.get('selected', False)]
        if not account_types:
            account_types = [a.get('id') for a in options.get('account_type')]
        date_from = options['date']['date_from']
        results = self.do_query(options, line_id)
        initial_bal_date_to = datetime.strptime(date_from, DF) + timedelta(days=-1)
        initial_bal_results = self.with_context(date_from=False, date_to=initial_bal_date_to.strftime(DF)).do_query(options, line_id)
        context = self.env.context
        base_domain = [('date', '<=', context['date_to']), ('company_id', 'in', context['company_ids']), ('account_id.internal_type', 'in', account_types)]
        base_domain.append(('date', '>=', date_from))
        if context['state'] == 'posted':
            base_domain.append(('move_id.state', '=', 'posted'))
        if options.get('unreconciled'):
            base_domain.append(('full_reconcile_id', '=', False))
        if context.get('account_ids', False):
            base_domain.append(('account_id', 'in', context.get('account_ids').ids))
        for partner_id, result in results.items():
            domain = list(base_domain)  # copying the base domain
            domain.append(('partner_id', '=', partner_id))

            partner = self.env['res.partner'].browse(partner_id).sudo()
            partners[partner] = result
            partners[partner]['initial_bal'] = initial_bal_results.get(partner.id, {'balance': 0, 'debit': 0, 'credit': 0})
            partners[partner]['balance'] += partners[partner]['initial_bal']['balance']
            if not context.get('print_mode'):
                partners[partner]['lines'] = self.env['account.move.line'].search(domain, order='date', limit=81)
            else:
                partners[partner]['lines'] = self.env['account.move.line'].search(domain, order='date')

        prec = self.env.company.currency_id.rounding
        missing_partner_ids = set(initial_bal_results.keys()) - set(results.keys())
        for partner_id in missing_partner_ids:
            if not float_is_zero(initial_bal_results[partner_id]['balance'], precision_rounding=prec):
                partner = self.env['res.partner'].browse(partner_id)
                partners[partner] = {'balance': 0, 'debit': 0, 'credit': 0}
                partners[partner]['initial_bal'] = initial_bal_results[partner_id]
                partners[partner]['balance'] += partners[partner]['initial_bal']['balance']
                partners[partner]['lines'] = self.env['account.move.line']

        return partners

    @api.model
    def get_lines(self, options, line_id=None):
        lines = []
        if line_id:
            line_id = line_id.replace('partner_', '')
        context = self.env.context

        # If a default partner is set, we only want to load the line referring to it.
        if options.get('partner_id'):
            line_id = options['partner_id']

        grouped_partners = self.group_by_partner_id(options, line_id)
        sorted_partners = sorted(grouped_partners, key=lambda p: p.name or '')
        unfold_all = context.get('print_mode') and not options.get('unfolded_lines') or options.get('partner_id')
        total_initial_balance = total_initial_debit = total_initial_credit = total_debit = total_credit = total_balance = total_end_debit = total_end_credit = 0.0
        for partner in sorted_partners:
            debit = grouped_partners[partner]['debit']
            credit = grouped_partners[partner]['credit']
            balance = grouped_partners[partner]['balance']
            initial_balance = grouped_partners[partner]['initial_bal']['balance']
            initial_debit = grouped_partners[partner]['initial_bal']['debit']
            initial_credit = grouped_partners[partner]['initial_bal']['credit']
            end_debit = balance if balance > 0 else 0
            end_credit = -balance if balance < 0 else 0
            total_initial_balance += initial_balance
            total_initial_debit += initial_debit
            total_initial_credit += initial_credit
            total_debit += debit
            total_credit += credit
            total_balance += balance
            total_end_debit += end_debit
            total_end_credit += end_credit
            lines.append({
                'id': 'partner_' + str(partner.id),
                'name': partner.name,
                'columns': [{'name': v} for v in [self.format_value(initial_debit),
                                                  self.format_value(initial_credit),
                                                  self.format_value(debit), 
                                                  self.format_value(credit), 
                                                  self.format_value(end_debit),
                                                  self.format_value(end_credit)]],
                'level': 2,
                'trust': partner.trust,
                'unfoldable': True,
                'unfolded': 'partner_' + str(partner.id) in options.get('unfolded_lines') or unfold_all,
                'colspan': 6,
            })
            if 'partner_' + str(partner.id) in options.get('unfolded_lines') or unfold_all:
                progress_debit = initial_balance if initial_balance > 0 else 0
                progress_credit = -initial_balance if initial_balance < 0 else 0
                progress_balance = initial_balance
                domain_lines = []
                amls = grouped_partners[partner]['lines']
                too_many = False
                if len(amls) > 80 and not context.get('print_mode'):
                    amls = amls[-80:]
                    too_many = True
                for line in amls:
                    line_debit = line.debit
                    line_credit = line.credit
                    progress_debit_before = progress_debit
                    progress_credit_before = progress_credit
                    progress_balance += (line_debit - line_credit)
                    progress_debit = progress_balance if progress_balance > 0 else 0
                    progress_credit = -progress_balance if progress_balance < 0 else 0
                    name = '-'.join(
                        (line.move_id.name not in ['', '/'] and [line.move_id.name] or []) +
                        (line.ref not in ['', '/', False] and [line.ref] or []) +
                        ([line.name] if line.name and line.name not in ['', '/'] else [])
                    )
                    if len(name) > 35 and not self.env.context.get('no_format'):
                        name = name[:32] + "..."
                    caret_type = 'account.move'
                    if line.move_id.move_type in ('in_refund', 'in_invoice'):
                        caret_type = 'account.invoice.in'
                    elif line.move_id.move_type in ('out_refund', 'out_invoice'):
                        caret_type = 'account.invoice.out'
                    elif line.payment_id:
                        caret_type = 'account.payment'
                    domain_lines.append({
                        'id': line.id,
                        'parent_id': 'partner_' + str(partner.id),
                        'name': line.date,
                        'columns': [{'name': v} for v in [line.journal_id.code, 
                                                        line.account_id.code, ', '.join(line.mapped('ctp_account_ids.code')), 
                                                        name, 
                                                        line.full_reconcile_id.name, 
                                                        self.format_value(progress_debit_before),
                                                        self.format_value(progress_credit_before),
                                                        self.format_value(line_debit),
                                                        self.format_value(line_credit),
                                                        self.format_value(progress_debit),
                                                        self.format_value(progress_credit)]],
                        'caret_options': caret_type,
                        'level': 4,
                    })
                if too_many:
                    domain_lines.append({
                        'id': 'too_many_' + str(partner.id),
                        'parent_id': 'partner_' + str(partner.id),
                        'action': 'view_too_many',
                        'action_id': 'partner,%s' % (partner.id,),
                        'name': _('There are more than 80 items in this list, click here to see all of them'),
                        'colspan': 1,
                        'columns': [{}],
                    })
                lines += domain_lines
        if not line_id:
            lines.append({
                'id': 'grouped_partners_total',
                'name': _('Total'),
                'level': 0,
                'class': 'o_af_reports_domain_total',
                'columns': [{'name': v} for v in ['', '', '', '', '', self.format_value(total_initial_debit),
                                                                        self.format_value(total_initial_credit),
                                                                        self.format_value(total_debit), 
                                                                        self.format_value(total_credit), 
                                                                        self.format_value(total_end_debit),
                                                                        self.format_value(total_end_credit)]],
            })
        return lines

    @api.model
    def get_report_name(self):
        return _('Partner Ledger')

    def set_context(self, options):
        ctx = super(ReportPartnerLedger, self).set_context(options)
        ctx['strict_range'] = True
        return ctx

