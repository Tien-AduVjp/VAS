from odoo import models, _
from odoo.exceptions import UserError


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    def _load_template(self, company, code_digits=None, account_ref=None, taxes_ref=None):
        """ Generate all the objects from the templates

            :param company: company the wizard is running for
            :param code_digits: number of digits the accounts code should have in the COA
            :param acc_ref: Mapping between ids of account templates and real accounts created from them
            :param taxes_ref: Mapping between ids of tax templates and real taxes created from them
            :returns: tuple with a dictionary containing
                * the mapping between the account template ids and the ids of the real accounts that have been generated
                  from them, as first item,
                * a similar dictionary for mapping the tax templates and taxes, as second item,
            :rtype: tuple(dict, dict, dict)
        """
        self.ensure_one()
        account_ref, taxes_ref = super(AccountChartTemplate, self)._load_template(company, code_digits, account_ref, taxes_ref)
        company.generate_vietnam_balance_carry_forward_rules()

        return account_ref, taxes_ref

    def _load(self, sale_tax_rate, purchase_tax_rate, company):
        bcfs = self.env['balance.carry.forward'].search([('company_id', '=', company.id)])
        if bcfs:
            raise UserError(_('Cannot load new chart of template for this company. There are some balance carry forwards existed, please remove them and try again.'))
        self.env['balance.carry.forward.rule'].search([('company_id', '=', company.id)]).unlink()
        res = super(AccountChartTemplate, self)._load(sale_tax_rate, purchase_tax_rate, company)
        return res


 