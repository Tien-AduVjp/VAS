# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    days_between_two_followups = fields.Integer(string='Number of days between two follow-ups', default=14)
    overdue_msg = fields.Text(string='Overdue Payments Message', translate=True,
        default=lambda s: _('''Dear Sir/Madam,

Our records indicate that some payments on your account are still due. Please find details below.
If the amount has already been paid, please disregard this notice. Otherwise, please forward us the total amount stated below.
If you have any queries regarding your account, Please contact us.

Thank you in advance for your cooperation.
Best Regards,'''))
    totals_below_sections = fields.Boolean(
        string='Add totals below sections',
        help='If checked, totals and subtotals appear below the sections of the report.')
#     property_report_financial_template = fields.Char(string='Report Financial Template',
#                                                      help='This template is used when displaying a financial report on backend')
#     property_report_financial_print_pdf_template = fields.Char(string='Report Financial Print PDF Template',
#                                                      help='This template is only used when printing a financial report to a PDF output')
