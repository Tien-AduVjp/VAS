from odoo import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def action_regenerate_analytic_lines(self):
        action = self.env.ref('viin_account_regenerate_analytic_line.act_regenerate_analytic_lines').read()[0]
        return action
