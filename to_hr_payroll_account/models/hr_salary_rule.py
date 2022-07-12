from odoo import fields, models


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    generate_account_move_line = fields.Boolean(string='Generate Journal Item', tracking=True,
                                               help="If checked, an accounting journal item will be generated"
                                               " for the result of this rule. You may need to specify credit account for the rule and debit"
                                               " account for the rule or expense account for the contract if you don't whant to use the debit"
                                               " account of the rule.")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', tracking=True,
                                          help="If specified, analytic items of this analytic account will be generated along with the"
                                          " corresponding general journal item. If not, the analytic account defined on the corresponding"
                                          " employee contract will be used, if specified on the contract.")
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    # TODO: rename anylytic_option into analytic_option
    anylytic_option = fields.Selection([
        ('none', 'None'),
        ('debit_account', 'Debit Account'),
        ('credit_account', 'Credit Account')],
        default='none', string='Analytic Option', required=True, tracking=True,
        help="This controls what account analytic line will be generated for this rule,\n"
        "* None: no analytic items will be generated for this rule,\n"
        "* Debit Account: an analytic line will be generated for the journal item of the Debit Account only,\n"
        "* Credit Account: an analytic line will be generated for the journal item of the Credit Account only."
        )
    account_tax_id = fields.Many2one('account.tax', 'Tax', tracking=True)
    
    # TODO: rename these with _id suffix for convention compliance
    account_debit = fields.Many2one('account.account', 'Debit Account', domain=[('deprecated', '=', False)], tracking=True,
                                    help="If not specified, either the expense account specified for the employee contract"
                                    " or employee contract department will be used instead.")
    account_credit = fields.Many2one('account.account', 'Credit Account', domain=[('deprecated', '=', False)], tracking=True)
    
    
    def _get_partner(self, credit_account, employee=None):
        """
        Get partner of the slip line to use in account move line
        """
        employee = employee or self.env['hr.employee']
        # use partner of salary rule or fallback on employee's address
        register_partner = self.register_id.partner_id
        partner = register_partner or employee.address_home_id
        if credit_account:
            if register_partner or self.account_credit.internal_type in ('receivable', 'payable'):
                return partner
        else:
            if register_partner or self.account_debit.internal_type in ('receivable', 'payable'):
                return partner
        return False
