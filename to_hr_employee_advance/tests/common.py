import logging
from datetime import datetime
from unittest.mock import patch
from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()

        # Account
        cls.accounts = cls.env['account.account'].search([('company_id', '=', cls.env.company.id)])
        account_type = cls.env.ref('account.data_account_type_receivable')
        cls.account_receivable = cls.env['account.account'].create({
            'name': 'Advances',
            'code': 141123,
            'reconcile': True,
            'user_type_id': account_type.id,
            'company_id': cls.env.company.id,
        })
        cls.account_expenses = cls.accounts.filtered(lambda a: a.code == '600000')

        # Create employee advance manager.
        cls.employee_advance_manager_user = cls.env['res.users'].with_context(no_reset_password=True, tracking_disable=True).create({
            'name': 'Manager',
            'login': 'manager',
            'groups_id': [(6, 0, cls.env.user.groups_id.ids),
                          (4, cls.env.ref('account.group_account_user').id),
                          (4, cls.env.ref('account.group_account_manager').id),
                          (4, cls.env.ref('to_hr_employee_advance.group_employee_advance_manager').id)],
        })

        # Shadow the current environment/cursor with one having the report user.
        # This is mandatory to test access rights.
        cls.env = cls.env(user=cls.employee_advance_manager_user)
        cls.cr = cls.env.cr

        chart_template = cls.env.ref('l10n_generic_coa.configurable_chart_template', raise_if_not_found=False)
        if not chart_template:
            _logger.warning("Test skipped because there is no chart of account defined ...")
            cls.skipTest(cls, "No Chart of account found")

        chart_template.try_loading(company=cls.env.company)

        # Create employee advance approver.
        cls.employee_advance_approver_user = cls.env['res.users'].with_context(no_reset_password=True, tracking_disable=True).create({
            'name': 'Approver',
            'login': 'approver',
            'groups_id': [(6, 0, [
                cls.env.ref('account.group_account_manager').id,
                cls.env.ref('to_hr_employee_advance.group_employee_advance_approver').id])],
        })

        # Create employee advance user.
        cls.employee_advance_user = cls.env['res.users'].with_context(no_reset_password=True, tracking_disable=True).create({
            'name': 'User',
            'login': 'User',
            'groups_id': [(6, 0, [
                cls.env.ref('account.group_account_manager').id,
                cls.env.ref('to_hr_employee_advance.group_employee_advance_user').id])],
        })

        # Create employee advance manager partner
        cls.employee_advance_manager_partner = cls.env['res.partner'].with_context(context_no_mail = {
            'no_reset_password': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'Manager Partner',
                'email': 'manager@example.viindoo.com',
                })

        # Create employee advance approver partner
        cls.employee_advance_approver_partner = cls.env['res.partner'].with_context(context_no_mail = {
            'no_reset_password': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'Approver Partner',
                'email': 'approver@example.viindoo.com',
            })

        # Create employee advance partner
        cls.employee_advance_partner = cls.env['res.partner'].with_context(context_no_mail = {
            'no_reset_password': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'User Partner',
                'email': 'user@example.viindoo.com',
            })

        # Create employee advance manager employee.
        cls.employee_advance_manager_employee = cls.env['hr.employee'].with_context(tracking_disable=True).create({
            'name': 'Manager Employee',
            'user_id': cls.employee_advance_manager_user.id,
            'address_home_id': cls.employee_advance_manager_partner.id,
            'property_advance_account_id': cls.account_receivable.id,
        })

        # Create employee advance approver employee.
        cls.employee_advance_approver_employee = cls.env['hr.employee'].with_context(tracking_disable=True).create({
            'name': 'Approver Employee',
            'user_id': cls.employee_advance_approver_user.id,
            'property_advance_account_id': cls.account_receivable.id,
        })

        # Create employee advance employee.
        cls.employee_advance_employee = cls.env['hr.employee'].with_context(tracking_disable=True).create({
            'name': 'User Employee',
            'user_id': cls.employee_advance_user.id,
            'property_advance_account_id': cls.account_receivable.id,
        })

        # Employee Advance Journal
        cls.advance_journal = cls.env['account.journal'].search([
            ('company_id', '=', cls.env.company.id),
            ('code', '=', 'EAJ'), ('is_advance_journal', '=', True)], limit=1)

        # Journal
        cls.journals = cls.env['account.journal'].search([('company_id', '=', cls.env.company.id)])
        cls.cash_journal = cls.journals.filtered(lambda j: not j.is_advance_journal and j.type == 'cash')[:1]
        cls.bank_journal = cls.journals.filtered(lambda j: not j.is_advance_journal and j.type == 'bank')[:1]
        cls.misc_journal = cls.journals.filtered(lambda j: not j.is_advance_journal and j.type == 'general')[:1]

    def _check_account_move_line(self, move_lines, debit_code, debit_amount, credit_code, credit_amount):
        """
        Check the accounts, amounts in the journal items
        """
        debit_line = move_lines.filtered(lambda m: m.debit > 0)[:1]
        credit_line = move_lines.filtered(lambda m: m.credit > 0)[:1]
        self.assertEqual(debit_line.account_id.code, debit_code, "Wrong debit account")
        self.assertEqual(credit_line.account_id.code, credit_code, "Wrong credit account")
        self.assertEqual(debit_line.debit, debit_amount, "Wrong debit amount")
        self.assertEqual(credit_line.credit, credit_amount, "Wrong credit amount")

    def patch_datetime_now(self, now):
        return patch('odoo.fields.Datetime.now', return_value=now)

    def patch_date_today(self, today):
        if isinstance(today, datetime):
            today = today.date()
        return patch('odoo.fields.Date.today', return_value=today)

    def patch_date_context_today(self, today):
        if isinstance(today, datetime):
            today = today.date()
        return patch('odoo.fields.Date.context_today', return_value=today)
