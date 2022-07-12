from odoo import fields, models, api


class DeferralCategory(models.Model):
    _name = 'cost.revenue.deferral.category'
    _description = 'Cost Revenue Deferral Category'

    name = fields.Char(string="Name", required=True)
    type = fields.Selection([
        ('cost', 'Cost'),
        ('revenue', 'Revenue')
    ], string="Type", required=True)
    journal_id = fields.Many2one('account.journal', string="Journal", required=True)
    deferred_account_id = fields.Many2one('account.account', string="Deferred Account", required=True,
                                          domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])
    recognition_account_id = fields.Many2one('account.account', string="Recognition Account", required=True,
                                             domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])
    account_disposal_deferral_id = fields.Many2one('account.account', string="Disposal Account",
                                                   domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])
    account_analytic_id = fields.Many2one('account.analytic.account', string="Analytic account")
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags', default=lambda self: self._get_default_analytic_tags(),
                                        help="For analytic distributions")
    method_time = fields.Selection([
        ('number', 'Number of Deferrals'),
        ('end', 'Ending Date'),
    ], string="Time Method", required=True, default='number')
    method_number = fields.Integer(string="Number of Deferrals", default=5)
    method_period = fields.Integer(string="One Entry Every", required=True, default=1)
    method_end = fields.Date(string="Ending Date")
    method = fields.Selection([
        ('linear', 'Linear'),
        ('degressive', 'Degressive'),
    ], string="Computation Method", required=True, default='linear')
    note = fields.Text(string="Note")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    auto_create_move = fields.Boolean(string="Auto-Posted Deferral", default=False,
                                      help="Check this if you want to automatically generate the deferral lines of running deferral and posted this category.")

    @api.model
    def _get_default_analytic_tags(self):
        """
        For potential inheritant
        """
        return self.env['account.analytic.tag']

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id:
                self.deferred_account_id = self.journal_id.default_account_id
