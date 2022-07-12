from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    legal_report_off = fields.Boolean(string='Excluded in Legal Reports',
                                      compute='_get_legal_report_off', store=True, readonly=False,
                                      groups='to_accounting_entry_report_flag.group_accounting_report_flag_manager',
                                      tracking=True,
                                      help="This field is for filtering in some legal reports")

    @api.depends('move_id.legal_report_off')
    def _get_legal_report_off(self):
        for r in self:
            r.legal_report_off = r.move_id.legal_report_off

    def action_flag_report_off(self):
        self.filtered(lambda x: x.legal_report_off == False).write({'legal_report_off': True})

    def action_flag_report_on(self):
        self.filtered(lambda x: x.legal_report_off == True).write({'legal_report_off': False})

    def copy_data(self, default=None):
        if default is None:
            default = {}
        default.update({'legal_report_off': self.sudo().legal_report_off})
        return super(AccountMoveLine, self).copy_data(default=default)
