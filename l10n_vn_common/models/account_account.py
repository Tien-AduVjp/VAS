from odoo import models, api, _
from odoo.exceptions import ValidationError, UserError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountAccount, self).create(vals_list)
        vn_charts = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        vn_accounts = res.filtered(lambda a: a.company_id.chart_template_id.id in vn_charts.ids)
        vn_accounts._fill_account_tag_for_vn_coa()
        return res

    def _fill_account_tag_for_vn_coa(self):
        """
        Fill account tag for the account if not specified.
        """
        vn_charts = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        all_account_tags = self.env['account.account.tag'].search([('code', '!=', False)])
        for r in self:
            if r.company_id.chart_template_id.id not in vn_charts.ids:
                raise ValidationError( _("Fill account tags only for accounts in the company that use the Vietnam COA."))
            if not r.tag_ids:
                account_tags = all_account_tags.filtered(lambda a: a.code.startswith(r.code[:3]) and a.code in r.code)
                if account_tags:
                    r.write({
                        'tag_ids': [(6, 0, account_tags.ids)]
                    })

    @api.model
    def _search_new_account_code(self, company, digits, prefix):
        default_account_code = self.env.context.get('default_account_code', '')
        vn_charts = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        if company.chart_template_id.id in vn_charts.ids and default_account_code:
            for num in range(1, 9):
                new_code = default_account_code + '-0' + str(num)
                rec = self.search([('code', '=', new_code), ('company_id', '=', company.id)], limit=1)
                if not rec:
                    return new_code
            raise UserError(_('Cannot generate an unused account code.'))
        else:
            return super(AccountAccount, self)._search_new_account_code(company, digits, prefix)
