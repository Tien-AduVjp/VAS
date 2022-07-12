from odoo import models, _


class AccountReportCoa(models.AbstractModel):
    _inherit = 'account.coa.report'

    def get_template_ref(self):
        return _('Template S06-DN')

    def get_templates(self):
        templates = super(AccountReportCoa, self).get_templates()
        templates['render_print_template'] = self.env.company.chart_template_id.sudo().coa_report_print_template or 'to_account_reports_l10n_vn.template_coa_report_print_vn'
        return templates
