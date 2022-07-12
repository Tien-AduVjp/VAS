from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    account_asset_ids = fields.One2many('account.asset.asset', 'invoice_id', string='Account Assets', 
                                        help="This field refers to assets that used when creating assets from a vendor bill")
    account_assets_count = fields.Integer(string='Assets Count', compute='_compute_account_assets_count')
    asset_depreciation_ids = fields.One2many('account.asset.depreciation.line', 'move_id', string='Assets Depreciation Lines', ondelete="restrict")
    revaluation_line_ids = fields.One2many('account.asset.revaluation.line', 'move_id', string='Revaluation Lines', ondelete="restrict")
    account_asset_id = fields.Many2one('account.asset.asset', string='Asset/Revenue Recognition', 
                                       help="This field refers to a sales invoice of asset, that used when selling a asset.", readonly=True)

    def _compute_account_assets_count(self):
        # invoice users always have read access to account.asset.asset
        # however, purchase users who can create bill does not have read access to account.asset.asset. So, sudo() is required here
        assets_data = self.env['account.asset.asset'].sudo().read_group([('invoice_id', 'in', self.ids)], ['invoice_id'], ['invoice_id'])
        mapped_data = dict([(dict_data['invoice_id'][0], dict_data['invoice_id_count']) for dict_data in assets_data])
        for r in self:
            r.account_assets_count = mapped_data.get(r.id, 0)

    def action_view_account_assets(self):
        account_asset_ids = self.mapped('account_asset_ids')
        action = self.env.ref('to_account_asset.action_account_asset_asset')
        result = action.read()[0]

        # choose the view_mode accordingly
        if len(account_asset_ids) > 1:
            result['domain'] = "[('invoice_id', 'in', " + str(self.ids) + ")]"
        else:
            res = self.env.ref('to_account_asset.view_account_asset_asset_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = account_asset_ids.id or False
        return result

    def action_cancel(self):
        res = super(AccountMove, self).action_cancel()
        self.env['account.asset.asset'].sudo().search([('invoice_id', 'in', self.ids)]).write({'active': False})
        return res

    def action_move_create(self):
        result = super(AccountMove, self).action_move_create()
        for inv in self:
            context = dict(self.env.context)
            # Within the context of an invoice,
            # this default value is for the type of the invoice, not the type of the asset.
            # This has to be cleaned from the context before creating the asset,
            # otherwise it tries to create the asset with the type of the invoice.
            context.pop('default_type', None)
            inv.invoice_line_ids.with_context(context).generate_assets()
        return result
    
    def action_post(self):
        for r in self.filtered(lambda r: r.name == '/'):
            if r.account_asset_id:
                depreciation_date = False
                depreciation_dates = r.account_asset_id.depreciation_line_ids.filtered(lambda line: line.move_check and line.move_id.state == 'posted').mapped('depreciation_date')
                if depreciation_dates:
                    depreciation_date = max(depreciation_dates)
                
                if not depreciation_date:
                    depreciation_date = r.account_asset_id.date_first_depreciation == 'manual' and r.account_asset_id.first_depreciation_date or r.account_asset_id.date
                
                if depreciation_date > r.date:
                    raise UserError(_("The Invoice Date cannot be set before First/Last Depreciation Date!"))
        return super(AccountMove, self).action_post()

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        for asset in self.revaluation_line_ids.asset_id:
            asset._compute_depreciation_board()
        return res

    def button_cancel(self):
        for move in self:
            for line in move.asset_depreciation_ids:
                line.move_posted_check = False
        return super(AccountMove, self).button_cancel()

    def post(self):
        for move in self:
            asset_depreciation_ids = move.asset_depreciation_ids.sorted(key='depreciation_date')
            asset = move.account_asset_id
            
            if asset_depreciation_ids:
                if move.date > fields.Date.today():
                    raise UserError(_("This move is configured to be auto-posted on %s") % move.date)
                
                asset = asset_depreciation_ids[0].asset_id
                
            if asset:
                first_depreciation_date = asset.date_first_depreciation == 'manual' and asset.first_depreciation_date or asset.date
                if first_depreciation_date > move.date:
                    raise UserError(_('The date cannot be set before first depreciation date!'))
        
        res = super(AccountMove, self).post()
        
        # TODOS: remove in Odoo 14
        invoices = self.filtered(lambda m: m.type in ('in_invoice', 'in_refund', 'out_invoice', 'out_refund'))
        context = dict(self.env.context)
        # Within the context of an invoice,
        # this default value is for the type of the invoice, not the type of the asset.
        # This has to be cleaned from the context before creating the asset,
        # otherwise it tries to create the asset with the type of the invoice.
        context.pop('default_type', None)
        invoices.invoice_line_ids.with_context(context).generate_assets()
        
        self.mapped('asset_depreciation_ids').post_lines_and_close_asset()
        for asset in self.revaluation_line_ids.asset_id:
            asset._compute_depreciation_board()
        return res
    
    def unlink(self):
        depreciation_line_ids = self.env['account.asset.depreciation.line']
        for move in self:
            asset_id = move.account_asset_id
            if asset_id:
                asset_id.message_post(body=_("Document re-opened."))
                asset_id.write({
                    'state': 'open',
                    })
                if asset_id.depreciation_line_ids:
                    last_depreciation_line_id = asset_id.depreciation_line_ids.sorted(key='depreciation_date')[-1]
                    last_depreciation_line_id.write({
                        'disposal': False,
                        })
                    if not move.env.context.get('do_not_recompute_depreciation_line', False):
                        depreciation_line_ids |= last_depreciation_line_id
        
        asset_ids = self.mapped('revaluation_line_ids').filtered(lambda line: line.move_id).mapped('asset_id')
        
        res = super(AccountMove, self).unlink()
        
        if depreciation_line_ids:
            asset_ids = asset_ids | depreciation_line_ids.mapped('asset_id')
            depreciation_line_ids.filtered(lambda line: not line.move_check).unlink()
        
        if asset_ids:
            for asset in asset_ids:
                    asset._compute_depreciation_board()
        
        return res
