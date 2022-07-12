from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    lines_count = fields.Integer(string='Journal Items Count', compute='_compute_lines_count',search='_search_lines_count')

    @api.depends('line_ids')
    def _compute_lines_count(self):
        lines_data = self.env['account.move.line'].read_group([('move_id', 'in', self.ids)],['move_id'],['move_id'])
        mapped_data = dict([(dict_data['move_id'][0], dict_data['move_id_count']) for dict_data in lines_data])
        for r in self:
            r.lines_count = mapped_data.get(r.id, 0)

    def _search_lines_count(self, operator, value):
        if operator in ['>', '<', '>=', '<=', '=', '!='] and isinstance(value, int):
            if isinstance(value, bool):
                value = int(value)
            sql="""SELECT move_id FROM account_move_line
                GROUP BY move_id
                HAVING COUNT(*) """+operator+' %s'
            self.env.cr.execute(sql,(value,))
            line_count = self.env.cr.fetchall()
            return[('id','in',[line[0] for line in line_count])]
        else:
            raise UserError(_('Unsupported operator'))
