from odoo import models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    def _update_promotion_voucher_properties_vietnam(self):
        """
        This is called by post_init_hook
        """
        PropertyObj = self.env['ir.property']
        AccountAccount = self.env['account.account']
        for r in self.filtered(lambda c: c.chart_template_id == self.env.ref('l10n_vn.vn_template')):
            if not r.property_promotion_voucher_profit_account_id:
                r.property_promotion_voucher_profit_account_id = AccountAccount.search([
                    ('code', 'like', '711' + '%'),
                    ('company_id', '=', r.id)
                    ], limit=1)
            if not r.property_promotion_voucher_loss_account_id:
                r.property_promotion_voucher_loss_account_id = AccountAccount.search([
                    ('code', 'like', '5211' + '%'),
                    ('company_id', '=', r.id)
                    ], limit=1)
            if not r.property_unearn_revenue_account_id:
                r.property_unearn_revenue_account_id = AccountAccount.search([
                    ('code', 'like', '3387' + '%'),
                    ('company_id', '=', r.id)], limit=1)

            todo_list = [  # Property Promotion Voucher Accounts
                'property_promotion_voucher_profit_account_id',
                'property_promotion_voucher_loss_account_id',
            ]
            for record in todo_list:
                account = getattr(r, record)
                value = account and 'account.account,' + str(account.id) or False
                if value:
                    vals = {
                        'value': value,
                    }
                    properties = PropertyObj.search([
                        ('name', '=', record),
                        ('company_id', '=', r.id),
                        ('res_id', '=', False)
                        ])
                    if properties:
                        # update the property
                        properties.write(vals)
