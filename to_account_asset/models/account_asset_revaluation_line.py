from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class AccountAssetRevaluationLine(models.Model):
    _name = 'account.asset.revaluation.line'
    _description = 'Revalution Line of Asset'


    name = fields.Char(string='Reason', required=True, index=True)
    sequence = fields.Integer(required=True)
    asset_id = fields.Many2one('account.asset.asset', string='Asset', required=True, ondelete='cascade')
    parent_state = fields.Selection(related='asset_id.state', string='State of Asset', readonly=False)
    value = fields.Float(string='Value', digits=0, required=True)
    method = fields.Selection([('decrease', 'Decrease'), ('increase', 'Increase')], string='Method', required=True)
    revaluation_date = fields.Date('Date of Revaluation', index=True)
    move_id = fields.Many2one('account.move', string='Revaluation Entry')
    move_check = fields.Boolean(compute='_compute_move_check', string='Status', store=True)
    move_posted_check = fields.Boolean(compute='_compute_move_posted_check', string='Posted', store=True)

    @api.model
    def _prepare_revaluation_line_vals(self, asset, name, value, method, revaluation_date):
        return {
            'asset_id': asset.id,
            'sequence': len(asset.revaluation_line_ids) + 1,
            'name': name,
            'value': value,
            'method': method,
            'revaluation_date': revaluation_date,
            }

    @api.depends('move_id.revaluation_line_ids')
    def _compute_move_check(self):
        for r in self:
            r.move_check = bool(r.move_id)

    @api.depends('move_id.state')
    def _compute_move_posted_check(self):
        for r in self:
            r.move_posted_check = True if r.move_id.state == 'posted' else False

    def create_move(self, post_move=True):
        move_obj = self.env['account.move']
        for r in self:
            if r.move_id:
                raise UserError(_('This revalution line is already linked to a journal entry. Please post or delete it.'))

            move_vals = r._prepare_move()
            move = move_obj.create(move_vals)
            r.write({'move_id': move.id, 'move_check': True})
            move_obj |= move
        if post_move and move_obj:
            move_obj._post()
        return move_obj

    def _prepare_move(self):
        self.ensure_one()
        category_id = self.asset_id.category_id
        analytic_account_id = self.asset_id.sudo().analytic_account_id
        analytic_tag_ids = self.asset_id.sudo().analytic_tag_ids
        company_currency = self.asset_id.company_id.currency_id
        current_currency = self.asset_id.currency_id
        prec = company_currency.decimal_places
        value = current_currency._convert(
            self.value, company_currency, self.asset_id.company_id, self.revaluation_date)

        debit_account_id = category_id.asset_account_id.id
        credit_account_id = self.asset_id.revaluation_increase_account_id.id or category_id.revaluation_increase_account_id.id
        if self.method == 'decrease':
            debit_account_id = self.asset_id.revaluation_decrease_account_id.id or category_id.revaluation_decrease_account_id.id
            credit_account_id = category_id.asset_account_id.id


        move_line_1 = {
            'name': self.name,
            'account_id': credit_account_id,
            'debit': 0.0 if float_compare(value, 0.0, precision_digits=prec) > 0 else -value,
            'credit': value if float_compare(value, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': self.asset_id.partner_id.id,
            'analytic_account_id': analytic_account_id.id if category_id.type == 'sale' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and -1.0 * self.value or 0.0,
        }

        move_line_2 = {
            'name': self.name,
            'account_id': debit_account_id,
            'credit': 0.0 if float_compare(value, 0.0, precision_digits=prec) > 0 else -value,
            'debit': value if float_compare(value, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': self.asset_id.partner_id.id,
            'analytic_account_id': analytic_account_id.id if category_id.type == 'purchase' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and self.value or 0.0,
        }
        move_vals = {
            'ref': self.asset_id.code,
            'date': self.revaluation_date or False,
            'journal_id': category_id.journal_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
        return move_vals

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        res = super(AccountAssetRevaluationLine, self).create(vals_list)
        res.create_move()
        return res

    def unlink(self):
        for r in self:
            if r.move_check and (r.move_id.state == 'posted' or (r.move_id.name != '/' and not self.env.context.get('force_delete', False))):
                raise UserError(_("You cannot delete posted revaluation lines."))
        return super(AccountAssetRevaluationLine, self).unlink()
