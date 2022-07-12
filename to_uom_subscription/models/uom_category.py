# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError


class UoMCategory(models.Model):
    _inherit = 'uom.category'

    concat_uom_name = fields.Boolean(string='Name Concatenation', default=False,
                                   help="If checked, the display name of Units of Measure of this category will be concatenated with the category's name")

    def unlink(self):
        uom_categ_subscription = self.env.ref('to_uom_subscription.uom_categ_subscription')
        uom_categ_subscription_user = self.env.ref('to_uom_subscription.uom_categ_subscription_user')
        if any(categ.id in (uom_categ_subscription + uom_categ_subscription_user).ids for categ in self):
            raise UserError(_("You cannot delete this UoM Category as it is used by the system."))
        return super(UoMCategory, self).unlink()

