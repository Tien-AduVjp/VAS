from odoo import models, _
from odoo.exceptions import UserError


class AccountAnalyticGroup(models.Model):
    _inherit = 'account.analytic.group'
    
    def unlink(self):
        if self.env.ref('to_fleet_accounting.analytic_group_vehicles') in self:
            raise UserError(_("You may not be able to delete the analytic group '%s' as it is required for generating"
                                " analytic account upon creating a vehicle.") % self.env.ref('to_fleet_accounting.analytic_group_vehicles').name)
        return super(AccountAnalyticGroup, self).unlink()
