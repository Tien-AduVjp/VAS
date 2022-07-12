from odoo import fields, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'account.bank.statement')], string='Attachments')
