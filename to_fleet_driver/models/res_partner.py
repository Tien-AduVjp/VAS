from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    license_ids = fields.One2many('fleet.driver.license', 'driver_id', string='Licenses')
    current_license_id = fields.Many2one('fleet.driver.license', compute='_compute_current_license_id', string='License', help="The current License of the driver")
    is_driver = fields.Boolean(string='Is a Driver', default=False, help="Check this box if this partner is a driver")


    @api.depends('license_ids', 'license_ids.state')
    def _compute_current_license_id(self):
        """ get the current license """
        for driver in self:
            license_ids = driver.license_ids.filtered(lambda l: l.state == 'confirmed')
            driver.current_license_id = license_ids and license_ids[0] or False
