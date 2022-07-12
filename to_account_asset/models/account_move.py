from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    account_asset_ids = fields.One2many('account.asset.asset', 'invoice_id', string='Account Assets',
                                        help="This field refers to assets that used when creating assets from a vendor bill")
    account_assets_count = fields.Integer(string='Assets Count', compute='_compute_account_assets_count')
    asset_depreciation_ids = fields.One2many('account.asset.depreciation.line', 'move_id', string='Assets Depreciation Lines')
    revaluation_line_ids = fields.One2many('account.asset.revaluation.line', 'move_id', string='Revaluation Lines')
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
        account_asset_ids = self.sudo().mapped('account_asset_ids')
        action = self.env['ir.actions.act_window']._for_xml_id('to_account_asset.action_account_asset_asset')

        # choose the view_mode accordingly
        if len(account_asset_ids) > 1:
            action['domain'] = "[('invoice_id', 'in', " + str(self.ids) + ")]"
        else:
            res = self.env.ref('to_account_asset.view_account_asset_asset_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = account_asset_ids.id or False
        return action

    def action_post(self):
        for r in self.filtered(lambda r: r.name == '/'):
            asset = r.sudo().account_asset_id
            if asset:
                depreciation_date = False
                depreciation_dates = asset.depreciation_line_ids.filtered(lambda line: line.move_check and line.move_id.state == 'posted').mapped('depreciation_date')
                if depreciation_dates:
                    depreciation_date = max(depreciation_dates)

                if not depreciation_date:
                    depreciation_date = asset.date_first_depreciation == 'manual' and asset.first_depreciation_date or asset.date

                if depreciation_date > r.date:
                    raise UserError(_("The Invoice Date cannot be set before First/Last Depreciation Date!"))
        return super(AccountMove, self).action_post()

    def button_draft(self):
        res = super(AccountMove, self).button_draft()

        for asset in self.sudo().revaluation_line_ids.asset_id:
            asset._compute_depreciation_board()
        return res

    def button_cancel(self):
        # archive asset that is in draft when cancelling a invoice
        self.env['account.asset.asset'].sudo().search([('invoice_id', 'in', self.ids)]).write({'active': False})

        for move in self:
            for line in move.sudo().asset_depreciation_ids:
                line.move_posted_check = False
        return super(AccountMove, self).button_cancel()

    def _post(self, soft=True):
        for move in self:
            asset_depreciation_ids = move.sudo().asset_depreciation_ids.sorted(key='depreciation_date')
            asset = move.sudo().account_asset_id

            if asset_depreciation_ids:
                asset = asset_depreciation_ids[0].asset_id

            if asset:
                first_depreciation_date = asset.date_first_depreciation == 'manual' and asset.first_depreciation_date or asset.date
                if first_depreciation_date > move.date:
                    raise UserError(_('The date cannot be set before first depreciation date!'))

        res = super(AccountMove, self)._post(soft=soft)

        invoices = self.filtered(lambda m: m.move_type == 'in_invoice')
        invoices.invoice_line_ids.sudo().generate_assets()

        self.sudo().mapped('asset_depreciation_ids').post_lines_and_close_asset()
        for asset in self.sudo().revaluation_line_ids.filtered(lambda l: l.move_id.state == 'posted').asset_id:
            asset._compute_depreciation_board()
        return res

    def unlink(self):
        depreciation_line_ids = self.env['account.asset.depreciation.line'].sudo()
        for move in self:
            asset_id = move.sudo().account_asset_id
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

        asset_ids = self.sudo().mapped('revaluation_line_ids').filtered(lambda line: line.move_id).mapped('asset_id')

        res = super(AccountMove, self).unlink()

        if depreciation_line_ids:
            asset_ids = asset_ids | depreciation_line_ids.mapped('asset_id')
            depreciation_line_ids.filtered(lambda line: not line.move_check).unlink()

        if asset_ids:
            for asset in asset_ids:
                    asset._compute_depreciation_board()

        return res
