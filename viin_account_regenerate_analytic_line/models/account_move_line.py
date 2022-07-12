from odoo import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def action_regenerate_analytic_lines(self):
        action = self.env['ir.actions.act_window']._for_xml_id('viin_account_regenerate_analytic_line.act_regenerate_analytic_lines')
        return action
