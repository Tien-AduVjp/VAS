from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    exclude_already_purchased_apps = fields.Boolean(string='Exclude Already-Purchased Apps', default=True,
                                                    help="If checked, when selling apps to this partner,"
                                                    " the Auto Load Apps Dependencies on sales orders of"
                                                    " this customer will exclude the apps that have been"
                                                    " sold and paid to the customer.")
