from odoo import models


class PersonalTaxRule(models.Model):
    _inherit = 'personal.tax.rule'

    def _set_apply_tax_base_deduction(self):
        """
        Override super and return False if country is Vietnam and policy is 'flat_rate'.
        Otherwise return super.
        """
        self.ensure_one()
        vietnam = self.env.ref('base.vn')
        if self.country_id == vietnam and self.personal_tax_policy == 'flat_rate':
            return False
        else:
            return super(PersonalTaxRule, self)._set_apply_tax_base_deduction()
