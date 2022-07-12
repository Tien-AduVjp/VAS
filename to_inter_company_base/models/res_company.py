from odoo import fields, models, SUPERUSER_ID


class ResCompany(models.Model):
    _inherit = 'res.company'

    intercompany_user_id = fields.Many2one("res.users", string="Inter-Company User", default=SUPERUSER_ID,
        help="Responsible user for creation of documents triggered by intercompany rules. The user should"
        " have full access rights to related document models (i.e. invoice, sales order, purchase order)"
        " of the current company. Otherwise, Odoo Bot will be used instead.")

