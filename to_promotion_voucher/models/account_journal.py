from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    voucher_payment = fields.Boolean(string='Voucher Payment method', help="If checked, this journal will be able to be used"
                                     " as a payment method to record payment using promotion voucher.\n"
                                     " You also need to set an Unearned Revenue account for both the Default Credit Account and"
                                     " the Default Debit Account of the journal.")

    @api.model
    def create_promotion_voucher_journals(self):
        Company = self.env['res.company']
        for company in Company.search([('chart_template_id', '!=', False)]):
            # Check if property exists for promotion voucher account journal exists
            PropertyObj = self.env['ir.property']
            properties = PropertyObj.search([('name', '=', 'property_promotion_voucher_journal'), ('company_id', '=', company.id)])
            AccountJournal = self.env['account.journal']

            # If not, check if you can find a journal that is already there with the same name, otherwise create one
            if not properties:
                voucher_journal_name = _('Promotion Voucher')
                journal_id = self.search([
                    ('name', '=', voucher_journal_name),
                    ('company_id', '=', company.id),
                    ('code', '=', 'PVJ')], limit=1)

                if not journal_id:
                    journal_id = AccountJournal.with_context(avoid_api_constrains=True).create({
                        'name': voucher_journal_name,
                        'type': 'cash',
                        'code': 'PVJ',
                        'company_id': company.id,
                        'show_on_dashboard': True,
                        'voucher_payment': True,
                        'sequence': 99,
                        })

                vals = {'name': 'property_promotion_voucher_journal',
                  'fields_id': self.env['ir.model.fields'].search([
                    ('name', '=', 'property_promotion_voucher_journal'),
                    ('model', '=', 'voucher.type'),
                    ('relation', '=', 'account.journal')], limit=1).id,
                  'company_id': company.id,
                  'value': 'account.journal,' + str(journal_id.id)}

                PropertyObj.create(vals)

            todo_list = [  # Property Promotion Voucher Accounts
                'property_promotion_voucher_profit_account_id',
                'property_promotion_voucher_loss_account_id',
            ]
            for record in todo_list:
                account = getattr(company, record)
                value = account and 'account.account,' + str(account.id) or False
                if value:
                    field_id = self.env['ir.model.fields'].search([
                      ('name', '=', record),
                      ('model', '=', 'voucher.type'),
                      ('relation', '=', 'account.account')
                    ], limit=1).id
                    vals = {
                        'name': record,
                        'company_id': company.id,
                        'fields_id': field_id,
                        'value': value,
                        'res_id': 'voucher.type,' + str(self.env.ref('to_promotion_voucher.voucher_type_generic').id),
                    }
                    properties = PropertyObj.search([('name', '=', record), ('company_id', '=', company.id), ('value_reference', '!=', False)])
                    if not properties:
                        # create the property
                        PropertyObj.create(vals)

    @api.onchange('voucher_payment')
    def onchange_voucher_payment(self):
        if self.voucher_payment:
            self.type = 'cash'

    @api.constrains('voucher_payment', 'type')
    def _check_constrains_voucher_payment_and_type(self):
        for r in self:
            if not r._context.get('avoid_api_constrains', False) and r.voucher_payment and r.type not in ('cash', 'bank'):
                raise ValidationError(_("A Voucher Payment Journal must be in type of either 'Cash' or 'Bank'"))
