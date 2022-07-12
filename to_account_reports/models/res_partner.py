# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import timedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    payment_next_action = fields.Text('Next Action', copy=False, company_dependent=True,
                                      help="Note regarding the next action.")
    payment_next_action_date = fields.Date('Next Action Date', copy=False, company_dependent=True,
                                           help="The date before which no action should be taken.")
    unreconciled_aml_ids = fields.One2many('account.move.line', 'partner_id', string='Unreconciled Journal Items', domain=[
        ('reconciled', '=', False),
        ('account_id.deprecated', '=', False),
        ('account_id.internal_type', '=', 'receivable')])
    total_due = fields.Monetary(compute='_compute_total_due', string="Total Due")

    def _compute_total_due(self):
        """ Returns the total due as will be displayed on the Followup Report """
        today = fields.Date.context_today(self)
        domain = self.get_followup_lines_domain(today)
        account_move_lines = self.env['account.move.line'].search(domain)
        for r in self:
            total_due = 0.0
            for aml in account_move_lines.filtered(lambda l: l.partner_id==r):
                total_due += aml.amount_residual
            r.total_due = total_due

    partner_ledger_label = fields.Char(compute='_compute_partner_ledger_label', help='The label to display on partner ledger button, in form view')

    def _compute_partner_ledger_label(self):
        res_partner_search_mode = self._context.get('res_partner_search_mode', False)
        for record in self:
            if res_partner_search_mode == 'customer':
                record.partner_ledger_label = _('Customer Ledger')
            elif res_partner_search_mode == 'supplier':
                record.partner_ledger_label = _('Supplier Ledger')
            else:
                record.partner_ledger_label = _('Partner Ledger')

    def get_partners_in_need_of_action(self, overdue_only=False):
        result = []
        today = fields.Date.context_today(self)
        partners = self.search([('payment_next_action_date', '>', today)])
        domain = partners.with_context(exclude_given_ids=True).get_followup_lines_domain(today, overdue_only=overdue_only, only_unblocked=True)
        query = self.env['account.move.line']._where_calc(domain)
        tables, where_clause, where_params = query.get_sql()
        sql = """SELECT "account_move_line".partner_id
                 FROM %s
                 WHERE %s GROUP BY "account_move_line".partner_id"""
        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for res in results:
            if res[0]:
                result.append(res[0])
        return self.browse(result).filtered(lambda r: r.total_due > 0)

    def get_followup_lines_domain(self, date, overdue_only=False, only_unblocked=False):
        domain = [
            ('reconciled', '=', False),
            ('account_id.deprecated', '=', False),
            ('account_id.internal_type', '=', 'receivable'),
            '|', ('debit', '!=', 0), ('credit', '!=', 0),
            ('company_id', '=', self.env.company.id),
            ('move_id.state', '=', 'posted'),
        ]
        if only_unblocked:
            domain += [('blocked', '=', False)]
        if self.ids:
            if 'exclude_given_ids' in self._context:
                domain += [('partner_id', 'not in', self.ids)]
            else:
                domain += [('partner_id', 'in', self.ids)]
        # adding the overdue lines
        overdue_domain = ['|', '&', ('date_maturity', '!=', False), ('date_maturity', '<', date), '&', ('date_maturity', '=', False), ('date', '<', date)]
        domain += overdue_domain
        if not overdue_only:
            domain += overdue_domain + ['|', ('next_action_date', '=', False), ('next_action_date', '<=', date)]
        return domain

    def update_next_action(self, batch=False):
        """Updates the next_action_date of the right account move lines"""
        today = fields.Datetime.now()
        next_action_date = today + timedelta(days=self.env.company.days_between_two_followups)
        next_action_date = next_action_date.strftime('%Y-%m-%d')
        today = fields.Date.context_today(self)
        domain = self.get_followup_lines_domain(today)
        aml = self.env['account.move.line'].search(domain)
        aml.write({'next_action_date': next_action_date})
        if batch:
            return self.env['res.partner']
        return

    def open_action_followup(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        ctx.update({
            'model': 'account.followup.report',
        })
        return {
                'name': _("Overdue Payments for %s") % self.display_name,
                'type': 'ir.actions.client',
                'tag': 'af_report_followup_generic',
                'context': ctx,
                'options': {'partner_id': self.id},
            }

    def open_partner_ledger(self):
        return {'type': 'ir.actions.client',
            'name': _('Partner Ledger'),
            'tag': 'af_report_generic',
            'options': {'partner_id': self.id},
            'ignore_session': 'both',
            'context': "{'model':'account.partner.ledger'}"}

    @api.returns('self', lambda value: value.id)
    def message_post(self, body='', subject=None, message_type='notification',
                     subtype=None, parent_id=False, attachments=None,
                     content_subtype='html', **kwargs):
        if parent_id:
            parent = self.env['mail.message'].browse(parent_id)
            followup_subtype = self.env.ref('to_account_reports.followup_logged_action')
            if subtype and parent.subtype_id == followup_subtype:
                subtype = 'to_account_reports.followup_logged_action'

        return super(ResPartner, self).message_post(
                body=body, subject=subject, message_type=message_type, subtype=subtype,
                parent_id=parent_id, attachments=attachments, content_subtype=content_subtype,
                **kwargs)
