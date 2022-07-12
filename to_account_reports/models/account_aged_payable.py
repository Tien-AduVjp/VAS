from odoo import models, _


class ReportAccountAgedPayable(models.AbstractModel):
    _name = "account.aged.payable"
    _description = "Aged Payable"
    _inherit = "account.aged.partner"

    def set_context(self, options):
        context = super(ReportAccountAgedPayable, self).set_context(options)
        context.update({
            'account_type': 'payable',
            'aged_balance': True
        })
        return context

    def get_report_name(self):
        return _("Aged Payable")

    def get_templates(self):
        templates = super(ReportAccountAgedPayable, self).get_templates()
        templates.update({
            'main_template': 'to_account_reports.template_aged_payable_report',
            'line_template': 'to_account_reports.line_template_aged_payable_report',
        })
        return templates

