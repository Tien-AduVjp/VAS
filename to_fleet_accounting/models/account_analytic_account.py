from odoo import models, _
from odoo.exceptions import UserError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def write(self, vals):
        if 'name' in vals and not self._context.get('vehicle_force_change_name', False):
            for r in self:
                related_vehicle = self.env['fleet.vehicle'].sudo().search([('analytic_account_id', '=', r.id)], limit=1)
                if related_vehicle:
                    raise UserError(_("You could not rename the analytic account '%s' into '%s' while it is till referred by the vehicle '%s'."
                                      " Instead, please change the name of the vehicle which will also change the account name accordingly.")
                                       % (r.name, vals['name'], related_vehicle.display_name))
        return super(AccountAnalyticAccount, self).write(vals)
