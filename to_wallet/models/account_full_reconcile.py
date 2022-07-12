from odoo import models, api


class AccountFullReconcile(models.Model):
    _inherit = 'account.full.reconcile'

    @api.model_create_multi
    def create(self, vals_list):
        """
        This override to ensure that we will not create full reconcile for move lines that have amount_residual other than zero
        that happens with wallet related move lines
        """
        last_vals_list = []
        for vals in vals_list:
            if 'reconciled_line_ids' in vals:
                aml_ids = vals['reconciled_line_ids'][0][2]
                amls = self.env['account.move.line'].browse(aml_ids).exists()
                if amls:
                    company_currency = amls[0].company_currency_id
                    if all(company_currency.is_zero(aml.amount_residual) for aml in amls):
                        last_vals_list.append(vals)
        return super(AccountFullReconcile, self).create(last_vals_list)

