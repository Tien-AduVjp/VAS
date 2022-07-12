from odoo import models, fields


class MailActivityType(models.Model):
    _inherit = 'mail.activity.type'

    category = fields.Selection(selection_add=[('approval_request', 'Approval')],
                                help="Actions may trigger specific behavior like opening calendar view or automatically"
                                " mark as done when a document is uploaded or approve the related approval request.")
