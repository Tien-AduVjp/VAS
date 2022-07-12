from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    account_move_line_ids = fields.One2many('account.move.line', 'stock_picking_id', string='Account Move Lines',
                                            groups='account.group_account_invoice')

    account_move_ids = fields.One2many('account.move', 'stock_picking_id', string='Journal Entries',
                                       groups='account.group_account_invoice')

    account_moves_count = fields.Integer(string='Journal Entries Count', compute='_compute_account_moves_count',
                                         groups='account.group_account_invoice')

    def _compute_account_moves_count(self):
        am_data = self.env['account.move'].sudo().read_group([('stock_picking_id', 'in', self.ids)], ['stock_picking_id'], ['stock_picking_id'])
        mapped_data = dict([(dict_data['stock_picking_id'][0], dict_data['stock_picking_id_count']) for dict_data in am_data])
        for r in self:
            r.account_moves_count = mapped_data.get(r.id, 0)

    def action_view_account_moves(self):
        account_move_ids = self.mapped('account_move_ids')
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_journal_line')

        # override the context to get rid of the default filtering
        action['context'] = {}

        if len(account_move_ids) > 1:
            action['domain'] = [('id', 'in', account_move_ids.ids)]
        elif len(account_move_ids) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = account_move_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
