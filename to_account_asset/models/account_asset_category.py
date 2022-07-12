from odoo import api, fields, models


class AccountAssetCategory(models.Model):
    _name = 'account.asset.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Asset Category'

    def _default_journal_id(self):
        return self.env['account.journal'].search([('company_id', '=', self.env.company.id), ('code', 'ilike', '%' + 'asset' + '%')], limit=1)

    @api.model
    def _get_default_revaluation_decrease_account_id(self):
        """
        For future potential inheritance
        @rtype: account.account record
        """
        return self.env['account.account']
       
    @api.model
    def _get_default_revaluation_increase_account_id(self):
        """
        For future potential inheritance
        @rtype: account.account record
        """
        return self.env['account.account']

    active = fields.Boolean(default=True)
    name = fields.Char(required=True, index=True, string="Asset Type")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
                                          groups='analytic.group_analytic_accounting',
                                          default=lambda self: self._get_default_analytic_account())
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tag',
                                        groups='analytic.group_analytic_tags',
                                        default=lambda self: self._get_default_analytic_tags())
    asset_account_id = fields.Many2one('account.account', string='Asset Account', required=True,
                                       domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
                                       tracking=True,
                                       help="The account that is used to record the purchase of the asset at its original price.")
    depreciation_account_id = fields.Many2one('account.account', string='Depreciation Entries: Asset Account', required=True,
                                              domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
                                              tracking=True,
                                              help="The account that is used in the depreciation entries, to decrease the asset value.")
    depreciation_expense_account_id = fields.Many2one('account.account', string='Depreciation Entries: Expense Account', required=True,
                                                      domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
                                                      tracking=True,
                                                      help="The account that is used in the periodical entries, to record a part of the asset as expense.")
    disposal_expense_account_id = fields.Many2one('account.account', string='Disposal Entries: Expense Account',
                                                       domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
                                                       tracking=True,
                                                       help="Account used in the disposal entries, to support different entries generation"
                                                       " method upon asset disposal according to VAS (i.e. account 811).\n"
                                                       "When no account is set here, the Expense Account will be used instead.")
    revaluation_decrease_account_id = fields.Many2one('account.account', string='Revaluation Entries: Decrease Asset Account',
                                                      default=lambda self: self._get_default_revaluation_decrease_account_id(),
                                                      domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
                                                      tracking=True,
                                                      help="Account used in the revaluation entries, to revaluation decrease a part of the asset.",
                                                      required=True)
    revaluation_increase_account_id = fields.Many2one('account.account', string='Revaluation Entries: Increase Asset Account', 
                                                      default=lambda self: self._get_default_revaluation_increase_account_id(),
                                                      domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
                                                      tracking=True,
                                                      help="Account used in the revaluation entries, to revaluation increase a part of the asset.",
                                                      required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, default=_default_journal_id)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    method = fields.Selection([('linear', 'Linear'), ('degressive', 'Degressive'), ('degressive_then_linear', 'Accelerated Degressive')], 
                              string='Computation Method',
                              required=True,
                              default='linear',
                              help="The method that is used to compute the amount of depreciation lines.\n"
                                   "  * Linear = Gross Value / Number of Depreciations\n"
                                   "  * Degressive = Residual Value * Degressive Factor\n"
                                   "  * Accelerated Degressive: Like Degressive but to keep minimum depreciation value equal to Linear value\n")
    method_number = fields.Integer(string='Number of Depreciations', default=5, help="Please enter the number of depreciations that is needed to depreciate your asset")
    method_period = fields.Integer(string='Period Length', default=1, help="Choose the time between 2 depreciations here, in months", required=True)
    method_progress_factor = fields.Float('Degressive Factor', default=0.3)
    method_time = fields.Selection([('number', 'Number of Entries'), ('end', 'Ending Date')], string='Time Method', required=True, default='number',
        help="Choose the method to use to compute the dates and number of entries.\n"
           "  * Number of Entries: Fix the number of entries and the time between 2 depreciations.\n"
           "  * Ending Date: Choose the time between 2 depreciations and the date the depreciations won't go beyond.")
    method_end = fields.Date('Ending date')
    prorata = fields.Boolean(string='Prorata Temporis', help='Indicates that the first depreciation entry for this asset have to be done from the asset date instead of the first January / Start date of fiscal year')
    open_asset = fields.Boolean(string='Auto-Confirm Assets', help="Check this if you want to automatically confirm the assets of this category when created by invoices.")
    group_entries = fields.Boolean(string='Group Journal Entries', help="Check this if you want to group the generated entries by categories.")
    type = fields.Selection([('sale', 'Sale: Revenue Recognition'), ('purchase', 'Purchase: Asset')], required=True, index=True, default='purchase')
    date_first_depreciation = fields.Selection([
        ('last_day_period', 'Based on Last Day of Month'),
        ('manual', 'Manual')],
        string='Depreciation Dates', default='manual', required=True,
        help='The way to compute the date of the first depreciation.\n'
             '  * Based on last day of month: The depreciation dates will be based on the last day of the month.\n'
             '  * Manual: You will need set manually depreciation dates.')
    account_asset_ids = fields.One2many('account.asset.asset', 'category_id', string='Assets')
    account_assets_count = fields.Integer(string='Assets Count', compute='_compute_account_assets_count')
    use_company_currency = fields.Boolean(string='Use Company Currency', default=True,
                                          help="If checked, the value of assets generated from invoices for this category"
                                          " will always be converted to company's currency")

    def _compute_account_assets_count(self):
        assets_data = self.env['account.asset.asset'].read_group([('category_id', 'in', self.ids)], ['category_id'], ['category_id'])
        mapped_data = dict([(dict_data['category_id'][0], dict_data['category_id_count']) for dict_data in assets_data])
        for r in self:
            r.account_assets_count = mapped_data.get(r.id, 0)

    def copy_data(self, default=None):
        if default is None:
            default = {}
        default.update({
            'analytic_account_id': self.sudo().analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.sudo().analytic_tag_ids.ids)],
            })
        return super(AccountAssetCategory, self).copy_data(default)

    def _get_default_analytic_account(self):
        """
        For future potential inheritance
        @rtype: account.analytic.account record
        """
        return self.env['account.analytic.account']

    @api.model
    def _get_default_analytic_tags(self):
        """
        For future potential inheritance
        @rtype: account.analytic.tag record
        """
        return self.env['account.analytic.tag']

    @api.onchange('asset_account_id')
    def onchange_account_asset(self):
        if not self.revaluation_increase_account_id:
            self.revaluation_increase_account_id = self.asset_account_id
        
        if self.type == "purchase":
            self.depreciation_account_id = self.asset_account_id
        elif self.type == "sale":
            self.depreciation_expense_account_id = self.asset_account_id
    
    @api.onchange('depreciation_expense_account_id')
    def _onchange_depreciation_expense_account_id(self):
        if not self.revaluation_decrease_account_id:
            self.revaluation_decrease_account_id = self.depreciation_expense_account_id

    @api.onchange('type')
    def onchange_type(self):
        if self.type == 'sale':
            self.prorata = True
            self.method_period = 1
        else:
            self.method_period = 12

    def action_view_account_assets(self):
        self.ensure_one()
        account_asset_ids = self.account_asset_ids
        action = self.env.ref('to_account_asset.action_account_asset_asset')
        result = action.read()[0]

        result['context'] = {'default_category_id': self.id}
        # choose the view_mode accordingly
        if len(account_asset_ids) > 1:
            result['domain'] = "[('category_id', 'in', %s)]" % str(self.ids)
        else:
            res = self.env.ref('to_account_asset.view_account_asset_asset_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = account_asset_ids.id or False
        return result

    @api.onchange('method_time')
    def _onchange_method_time(self):
        if self.method_time != 'number':
            self.prorata = False

