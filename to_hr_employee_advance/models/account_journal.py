from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_advance_journal = fields.Boolean(string='Employee Advance Journal?', help="Check this to enable this journal for employee advance.")
