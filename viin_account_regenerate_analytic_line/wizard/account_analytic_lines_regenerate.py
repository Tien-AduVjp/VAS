from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountAnalyticLinesRegenerate(models.TransientModel):
    _name = 'account.analytic.lines.regenerate'
    _description  = 'Regenerate Analytic Lines' 

    def _get_default_account_move_lines(self):
        return self.env['account.move.line'].browse(self._context.get('active_ids'))
    
    def _get_default_analytic_tags(self):
        move_lines = self.env['account.move.line'].browse(self._context.get('active_ids'))
        if move_lines.exists() and len(move_lines) == 1:
            return move_lines.analytic_tag_ids
        
    account_move_line_ids = fields.Many2many('account.move.line', default=_get_default_account_move_lines, required=True)
    account_move_lines_count = fields.Integer(string='Move Lines Count', compute='_compute_account_move_lines_count')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags', default=_get_default_analytic_tags)
    forced_regenerate = fields.Boolean(string='Forced Regenerate', default=False, help="if checked, every chosen journal item (with or without an analytic line) "
                                                                                "will get regenerated a new one by the system")
    
    @api.depends('account_move_line_ids')
    def _compute_account_move_lines_count(self):
        for r in self:
            r.account_move_lines_count = len(r.account_move_line_ids)
    
    def _prepare_log_body_values(self, moves, move_lines):
        self.ensure_one()
        result = {}
        for move in moves:
            lines = move_lines.filtered(lambda l: l.move_id == move)
            body = '<div class="o_thread_message_content"><ul class="o_mail_thread_message_tracking">'
            for line in lines:
                body += '<li>'
                body += _('Journal Item (Account: %s, Debit: %s, Credit: %s) <br/>') % (line.account_id.display_name, line.debit, line.credit)
                body += _('Analytic Account: %s <span class="fa fa-long-arrow-right" role="img" aria-label="Changed" title="Changed"/> %s <br/>') % (line.analytic_account_id.name, self.analytic_account_id.name)
                body += '</li>'
            body += '</ul></div>'
            result[move.id] = body
        return result

    def _prepare_mass_log_values(self, moves, move_lines):
        self.ensure_one()
        return {
            'bodies': self._prepare_log_body_values(moves, move_lines),
        }
    
    def regeneate_analytic_lines(self):
        for r in self:
            to_update_move_lines = r.account_move_line_ids.filtered(
                lambda line: \
                line.move_id.state == 'posted'
                and (
                    line.analytic_account_id != r.analytic_account_id 
                    or (
                        line.analytic_account_id == r.analytic_account_id
                        and not line.analytic_line_ids
                        )
                    or (
                        line.analytic_line_ids
                        and r.analytic_account_id.id not in line.analytic_line_ids.account_id.ids
                        )
                    )
                )
            if not to_update_move_lines:
                continue
            if not r.forced_regenerate:
                existing_analytic_lines = to_update_move_lines.filtered(lambda line: line.analytic_line_ids)
                if existing_analytic_lines:
                    raise ValidationError(_("The journal item `%s` already had an analytic line. Please either exclude it or check the option"
                        " 'Forced Regenerate' to remove the existing and generate new one.") % ", ".join(existing_analytic_lines.mapped('display_name')))
            moves = to_update_move_lines.mapped('move_id')
            #Log note on account moves document
            log_values = r._prepare_mass_log_values(moves, to_update_move_lines)
            moves._message_log_batch(**log_values)
            moves.write({'to_check': True})
            to_update_move_lines.mapped('analytic_line_ids').unlink()
            vals_to_update = {'analytic_account_id': r.analytic_account_id.id}
            if r.account_move_lines_count == 1:
                vals_to_update.update({'analytic_tag_ids': [(6, 0, r.analytic_tag_ids.ids)]})
            to_update_move_lines.write(vals_to_update)
            to_update_move_lines.create_analytic_lines()

