import logging

from odoo.tests import SavepointCase, Form

_logger = logging.getLogger(__name__)


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()

        chart_template = cls.env.ref('l10n_generic_coa.configurable_chart_template', raise_if_not_found=False)
        if not chart_template:
            _logger.warning("Test skipped because there is no chart of account defined ...")
            cls.skipTest(cls, "No Chart of account found")

        cls.partner = cls.env.ref('base.res_partner_1')

        cls.expense_sheet = cls.env.ref('hr_expense.office_furniture_sheet')
        cls.expense_sheet.expense_line_ids.write({
            'to_invoice': True,
            'vendor_id': cls.partner.id,
            'currency_id': cls.env.company.currency_id.id
            })

        cls.expense_sheet.write({
            'bank_journal_id': cls.env.company.bank_journal_ids[:1].id,
            'currency_id': cls.env.company.currency_id.id
            })

    def post_hr_expense_sheet(self, expense_sheet):
        expense_sheet.action_submit_sheet()
        expense_sheet.approve_expense_sheets()
        expense_sheet.action_sheet_move_create()
        return expense_sheet

    def register_payment_hr_expense_sheet_employee_paid(self, expense_sheet):
        posted_expense_sheet = self.post_hr_expense_sheet(expense_sheet)
        wz_payment_form = Form(self.env['hr.expense.sheet.register.payment.wizard'].with_context(default_payment_type='inbound',
                                                                          active_ids=[posted_expense_sheet.id],
                                                                          active_id=posted_expense_sheet.id,
                                                                          active_model='hr.expense.sheet',
                                                                          default_amount=posted_expense_sheet.total_amount,
                                                                          partner_id=posted_expense_sheet.address_id))
        wz_payment_form.journal_id = self.env.company.bank_journal_ids[:1]
        wz_payment = wz_payment_form.save()
        wz_payment.expense_post_payment()
        return expense_sheet.payment_ids

    def cancel_hr_expense_sheet_posted(self, expense_sheet):
        self.env['hr.expense.refuse.wizard'].with_context(hr_expense_refuse_model='hr.expense.sheet',
                                                          active_ids=[expense_sheet.id],
                                                          active_id=expense_sheet.id) \
                                            .create({'reason': 'Mistake'}).expense_refuse_reason()
