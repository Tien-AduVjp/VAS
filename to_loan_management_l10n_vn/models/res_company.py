from odoo import models, api, _
import logging
_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def _update_vn_params(self):
        # if we already have a Vietnam coa installed, update journal and set property field
        vn_chart_id = self.env.ref('l10n_vn.vn_template', raise_if_not_found=False)
        if vn_chart_id:
            AccountAccount = self.env['account.account']
            AccountJournal = self.env['account.journal']
            for company in self.filtered(lambda r:r.chart_template_id == vn_chart_id):
                acc_3411 = AccountAccount.search([('company_id', '=', company.id), ('code', '=like', '3411' + '%')], limit=1)
                acc_1283 = AccountAccount.search([('company_id', '=', company.id), ('code', '=like', '1283' + '%')], limit=1)
                acc_635 = AccountAccount.search([('company_id', '=', company.id), ('code', '=like', '635' + '%')], limit=1)
                acc_515 = AccountAccount.search([('company_id', '=', company.id), ('code', '=like', '515' + '%')], limit=1)
                acc_131 = AccountAccount.search([('company_id', '=', company.id), ('code', '=like', '131' + '%')], limit=1)
                acc_331 = AccountAccount.search([('company_id', '=', company.id), ('code', '=like', '331' + '%')], limit=1)

                borrows_journal = AccountJournal.search([('name', 'ilike', '%' + _('Borrowing Loans Journal') + '%'), ('company_id', '=', company.id), ('type', '=', 'purchase')], limit=1)
                lends_journal = AccountJournal.search([('name', 'ilike', '%' + _('Lending Loans Journal') + '%'), ('company_id', '=', company.id), ('type', '=', 'sale')], limit=1)

                # Update company
                update_comp_data = {}
                if not company.loan_borrowing_account_id and acc_3411:
                    update_comp_data['loan_borrowing_account_id'] = acc_3411.id
                if not company.loan_borrowing_journal_id and borrows_journal:
                    update_comp_data['loan_borrowing_journal_id'] = borrows_journal.id
                if not company.loan_lending_account_id and acc_1283:
                    update_comp_data['loan_lending_account_id'] = acc_1283.id
                if not company.loan_lending_journal_id and lends_journal:
                    update_comp_data['loan_lending_journal_id'] = lends_journal.id
                if bool(update_comp_data):
                    company.write(update_comp_data)

                # update journals
                if borrows_journal:
                    if not borrows_journal.default_account_id:
                        borrows_journal.write({
                            'default_account_id': acc_3411.id,
                            'account_control_ids': [(6,0,(acc_3411|acc_331|acc_635).ids)],
                        })
                if lends_journal:
                    if not lends_journal.default_account_id:
                        lends_journal.write({
                            'default_account_id': acc_1283.id,
                            'account_control_ids': [(6,0,(acc_1283|acc_131|acc_515).ids)],
                        })

                # update product
                product_cat_id = self.env.ref('to_loan_management.product_category_loan_interest', raise_if_not_found=False)
                if product_cat_id:
                    PropertyObj = self.env['ir.property']
                    IrModelField = self.env['ir.model.fields']
                    product_cat_id_res_id = 'product.category,' + str(product_cat_id.id)

                    # loan expense
                    expense_account_val_ref = 'account.account,' + str(acc_635.id)
                    field_property_account_expense_categ_id = IrModelField.search([
                        ('name', '=', 'property_account_expense_categ_id'),
                        ('model', '=', 'product.category'),
                        ('relation', '=', 'account.account')], limit=1)

                    properties = PropertyObj.search([
                        ('name', '=', 'property_account_expense_categ_id'),
                        ('res_id', '=', product_cat_id_res_id),
                        ('fields_id', '=', field_property_account_expense_categ_id.id),
                        ('value_reference', '=', expense_account_val_ref),
                        ('company_id', '=', company.id)])

                    if not properties:
                        PropertyObj.create({
                            'name':'property_account_expense_categ_id',
                            'fields_id': field_property_account_expense_categ_id.id,
                            'res_id': product_cat_id_res_id,
                            'value_reference':expense_account_val_ref,
                            'company_id': company.id,
                            'type':'many2one',
                        })

                    # loan income
                    income_account_val_ref = 'account.account,' + str(acc_515.id)
                    field_property_account_income_categ_id = IrModelField.search([
                        ('name', '=', 'property_account_income_categ_id'),
                        ('model', '=', 'product.category'),
                        ('relation', '=', 'account.account')], limit=1)

                    properties = PropertyObj.search([
                        ('name', '=', 'property_account_income_categ_id'),
                        ('res_id', '=', product_cat_id_res_id),
                        ('fields_id', '=', field_property_account_income_categ_id.id),
                        ('value_reference', '=', income_account_val_ref),
                        ('company_id', '=', company.id)])

                    if not properties:
                        PropertyObj.create({
                            'name':'property_account_income_categ_id',
                            'fields_id': field_property_account_income_categ_id.id,
                            'res_id': product_cat_id_res_id,
                            'value_reference': income_account_val_ref,
                            'company_id': company.id,
                            'type':'many2one',
                        })
