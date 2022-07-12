from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = "res.users"

    def today(self):
        """
        For usage in xml domain filters. For example [('date_published','&lt;=',user.today()]
        """
        return fields.Date.today()
