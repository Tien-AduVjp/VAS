from odoo import api, models, fields, _


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    property_promotion_voucher_profit_account_id = fields.Many2one('account.account.template', string='Voucher Profit Account')
    property_promotion_voucher_loss_account_id = fields.Many2one('account.account.template', string='Voucher Loss Account')
    property_unearn_revenue_account_id = fields.Many2one('account.account.template', string='Unearn Revenue Account')

    def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
        """
        @param acc_template_ref: Mapping between ids of account templates and real accounts created from them
        @param company: company record
        @param journals_dict: list of journal vals dicts
        @return: list of journal vals dicts
        """
        journal_data = super(AccountChartTemplate, self)._prepare_all_journals(
            acc_template_ref=acc_template_ref,
            company=company,
            journals_dict=journals_dict
            )
        journal_data.append({
            'name': _('Promotion Voucher'),
            'type': 'general',
            'code': 'PVJ',
            'show_on_dashboard': True,
            'sequence': 11,
            'voucher_payment':True,
            'company_id':company.id,
            'default_debit_account_id': acc_template_ref.get(self.property_unearn_revenue_account_id.id),
            'default_credit_account_id': acc_template_ref.get(self.property_unearn_revenue_account_id.id),
            })
        return journal_data

    def generate_properties(self, acc_template_ref, company, property_list=None):
        res = super(AccountChartTemplate, self).generate_properties(acc_template_ref=acc_template_ref, company=company)
        PropertyObj = self.env['ir.property']  # Property Promotion Voucher Journal
        value = self.env['account.journal'].search([('company_id', '=', company.id), ('code', '=', 'PVJ'), ('type', 'in', ('cash', 'bank'))], limit=1)
        if value:
            field = self.env['ir.model.fields'].search([('name', '=', 'property_promotion_voucher_journal'), ('model', '=', 'voucher.type'), ('relation', '=', 'account.journal')], limit=1)
            vals = {
                'name': 'property_promotion_voucher_journal',
                'company_id': company.id,
                'fields_id': field.id,
                'value': 'account.journal,%s' % value.id,
            }
            properties = PropertyObj.search([('name', '=', 'property_promotion_voucher_journal'), ('company_id', '=', company.id)])
            if properties:
                # the property exist: modify it
                properties.write(vals)
            else:
                # create the property
                PropertyObj.create(vals)

        todo_list = [  # Property Promotion Voucher Accounts
            'property_promotion_voucher_profit_account_id',
            'property_promotion_voucher_loss_account_id',
        ]
        for record in todo_list:
            account = getattr(self, record)
            value = account and 'account.account,' + str(acc_template_ref[account.id]) or False
            if value:
                field = self.env['ir.model.fields'].search([('name', '=', record),
                                                            ('model', '=', 'voucher.type'),
                                                            ('relation', '=', 'account.account')], limit=1)
                vals = {
                    'name': record,
                    'company_id': company.id,
                    'fields_id': field.id,
                    'value': value,
                }
                properties = PropertyObj.search([('name', '=', record), ('company_id', '=', company.id)])
                if properties:
                    # the property exist: modify it
                    properties.write(vals)
                else:
                    # create the property
                    PropertyObj.create(vals)

        return res
    
    @api.model
    def generate_journals(self, acc_template_ref, company, journals_dict=None):
        res = super(AccountChartTemplate, self.with_context(avoid_api_constrains=True)).generate_journals(acc_template_ref, company, journals_dict=journals_dict)
        company._update_promotion_voucher_journal_if_exists()
        return res
