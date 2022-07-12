from odoo import models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    def _update_promotion_voucher_properties_vietnam(self):
        """
        This is called by post_init_hook
        """
        PropertyObj = self.env['ir.property']
        AccountAccount = self.env['account.account']
        AccountJournal = self.env['account.journal']
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

            journal_id = AccountJournal.search([
                ('name', '=', _('Promotion Voucher')),
                ('company_id', '=', r.id),
                ('type', 'in', ('cash', 'bank')),
                ('voucher_payment', '=', True)], limit=1)
            if journal_id:
                update_data = {}
                bank_and_cash_type = self.env.ref('account.data_account_type_liquidity')
                if not journal_id.default_debit_account_id or journal_id.default_debit_account_id.user_type_id == bank_and_cash_type:
                    update_data['default_debit_account_id'] = r.property_unearn_revenue_account_id.id
                if not journal_id.default_credit_account_id or journal_id.default_credit_account_id.user_type_id == bank_and_cash_type:
                    update_data['default_credit_account_id'] = r.property_unearn_revenue_account_id.id
                if bool(update_data):
                    journal_id.write(update_data)

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
