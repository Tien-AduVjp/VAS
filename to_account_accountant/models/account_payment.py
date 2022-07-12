from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'account.payment')], string='Attachments')

    # override to add tracking
    state = fields.Selection(tracking=True)
