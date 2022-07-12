# -*- coding: utf-8 -*-
from odoo import models, api, _
import logging
_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def _update_vn_params(self):
        AccountAccount = self.env['account.account']
        # if we already have a Vietnam coa installed, update journal and set property field
        vn_chart_id = self.env.ref('l10n_vn.vn_template', raise_if_not_found=False)
        if vn_chart_id:
            PropertyObj = self.env['ir.property']
            AccountJournal = self.env['account.journal']
            IrModelField = self.env['ir.model.fields']
            for company_id in self.search([('chart_template_id', '=', vn_chart_id.id)]):
                acc_3411 = AccountAccount.search([('company_id', '=', company_id.id), ('code', 'like', '3411' + '%')], limit=1)
                acc_1283 = AccountAccount.search([('company_id', '=', company_id.id), ('code', 'like', '1283' + '%')], limit=1)
                borrows_journal_id = AccountJournal.search([('name', 'ilike', '%' + _('Borrowing Loans Journal') + '%'), ('company_id', '=', company_id.id), ('type', '=', 'purchase')], limit=1)
                lends_journal_id = AccountJournal.search([('name', 'ilike', '%' + _('Lending Loans Journal') + '%'), ('company_id', '=', company_id.id), ('type', '=', 'sale')], limit=1)
                update_comp_data = {}
                if not company_id.loan_borrowing_account_id and acc_3411:
                    update_comp_data['loan_borrowing_account_id'] = acc_3411.id
                if not company_id.loan_borrowing_journal_id and borrows_journal_id:
                    update_comp_data['loan_borrowing_journal_id'] = borrows_journal_id.id
                if not company_id.loan_lending_account_id and acc_1283:
                    update_comp_data['loan_lending_account_id'] = acc_1283.id
                if not company_id.loan_lending_journal_id and lends_journal_id:
                    update_comp_data['loan_lending_journal_id'] = lends_journal_id.id
                if bool(update_comp_data):
                    company_id.write(update_comp_data)
                expense_account_id = AccountAccount.search([('company_id', '=', company_id.id), ('code', 'like', '635' + '%')], limit=1)
                income_account_id = AccountAccount.search([('company_id', '=', company_id.id), ('code', 'like', '515' + '%')], limit=1)

                if borrows_journal_id:
                    update_data = {}
                    if not borrows_journal_id.default_debit_account_id:
                        update_data['default_debit_account_id'] = acc_3411.id
                    if not borrows_journal_id.default_credit_account_id:
                        update_data['default_credit_account_id'] = acc_3411.id
                    if bool(update_data):
                        borrows_journal_id.write(update_data)

                if lends_journal_id:
                    update_data = {}
                    if not lends_journal_id.default_debit_account_id:
                        update_data['default_debit_account_id'] = acc_1283.id
                    if not lends_journal_id.default_credit_account_id:
                        update_data['default_credit_account_id'] = acc_1283.id
                    if bool(update_data):
                        lends_journal_id.write(update_data)

                product_cat_id = self.env.ref('to_loan_management.product_category_loan_interest', raise_if_not_found=False)
                if product_cat_id:
                    product_cat_id_res_id = 'product.category,' + str(product_cat_id.id)

                    expense_account_val_ref = 'account.account,' + str(expense_account_id.id)
                    field_property_account_expense_categ_id = IrModelField.search([
                        ('name', '=', 'property_account_expense_categ_id'),
                        ('model', '=', 'product.category'),
                        ('relation', '=', 'account.account')], limit=1)

                    properties = PropertyObj.search([
                        ('name', '=', 'property_account_expense_categ_id'),
                        ('res_id', '=', product_cat_id_res_id),
                        ('fields_id', '=', field_property_account_expense_categ_id.id),
                        ('value_reference', '=', expense_account_val_ref),
                        ('company_id', '=', company_id.id)])

                    if not properties:
                        new_prop = PropertyObj.create({
                            'name':'property_account_expense_categ_id',
                            'fields_id': field_property_account_expense_categ_id.id,
                            'res_id': product_cat_id_res_id,
                            'value_reference':expense_account_val_ref,
                            'company_id': company_id.id,
                            'type':'many2one',
                        })

                    # loan income
                    income_account_val_ref = 'account.account,' + str(income_account_id.id)
                    field_property_account_income_categ_id = IrModelField.search([
                        ('name', '=', 'property_account_income_categ_id'),
                        ('model', '=', 'product.category'),
                        ('relation', '=', 'account.account')], limit=1)

                    properties = PropertyObj.search([
                        ('name', '=', 'property_account_income_categ_id'),
                        ('res_id', '=', product_cat_id_res_id),
                        ('fields_id', '=', field_property_account_income_categ_id.id),
                        ('value_reference', '=', income_account_val_ref),
                        ('company_id', '=', company_id.id)])

                    if not properties:
                        new_prop = PropertyObj.create({
                            'name':'property_account_income_categ_id',
                            'fields_id': field_property_account_income_categ_id.id,
                            'res_id': product_cat_id_res_id,
                            'value_reference': income_account_val_ref,
                            'company_id': company_id.id,
                            'type':'many2one',
                        })              
                    
                    
                    
                    
                    
