import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _generate_general_employee_payable_account(self):
        super(ResCompany, self)._generate_general_employee_payable_account()
        self._generate_vietnam_employee_advance_account()

    def _generate_vietnam_employee_advance_account(self):
        vietnam_coa_templates = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        for r in self.filtered(lambda c: c.chart_template_id.id in vietnam_coa_templates.ids):
            account_141 = self.env['account.account'].search([
                ('company_id', '=', r.id),
                ('deprecated', '=', False),
                ('code', 'ilike', '141%'),
                ('internal_type', '=', 'receivable')], limit=1)
            fields_advance = self.env['ir.model.fields'].search([
                ('name', '=', 'property_advance_account_id'),
                ('model', '=', 'hr.employee'),
                ('ttype', '=', 'many2one'),
                ('relation', '=', 'account.account')], limit=1)
            if account_141 and fields_advance:
                property_advance = self.env['ir.property'].search([
                    ('fields_id', '=', fields_advance.id),
                    ('company_id', '=', r.id)])
                if property_advance:
                    property_advance.write({
                        'name': 'property_advance_account_id',
                        'value_reference': '%s,%d' % (account_141._name, account_141.id)
                    })
                else:
                    self.env['ir.property'].create({
                        'name': 'property_advance_account_id',
                        'fields_id': fields_advance.id,
                        'company_id': r.id,
                        'value_reference': '%s,%d' % (account_141._name, account_141.id)
                    })

    def _generate_advance_account(self):
        # TODO: remove me in master/15+
        _logger.warning("The method `_generate_advance_account()` is deprecated and will be removed soon. Please use the `_generate_vietnam_employee_advance_account()` instead.")
        self._generate_vietnam_employee_advance_account()

    def _apply_vietnam_empoloyee_payable_account(self):
        for r in self._filter_vietnam_coa():
            account = self.env['account.account'].search([('code', '=ilike', '334' + '%'), ('company_id', '=', r.id)], limit=1)
            r.write({
                'general_employee_payable_account_id': account.id
            })

    def _update_vietnam_employee_payable_account(self):
        # employee payable account for companies
        self._apply_vietnam_empoloyee_payable_account()
        # employee payable account for employees
        self.env['hr.employee'].sudo().search([])._apply_vietnam_empoloyee_payable_account()

    def _l10n_vn_update_departments_expense_account(self):
        """
        To be called by post_init_hook
        self = companies (VN CoA TT 133/200)
        """
        for r in self._filter_vietnam_coa():
            departments = self.env['hr.department'].sudo().with_context(active_test=False).search([
                ('company_id', '=', r.id), ('account_expense_id', '=', False)])
            account = self.env['account.account'].search([
                ('company_id', '=', r.id),
                ('code', '=ilike', '642' + '%'), ('deprecated', '=', False)], limit=1)
            if account and departments:
                departments.write({'account_expense_id': account.id})
