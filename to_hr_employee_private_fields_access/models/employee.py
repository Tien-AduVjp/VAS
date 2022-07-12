from odoo import models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def sudo_address_home_id(self):
        """
        Since the access to the address_home_id is restricted to hr.group_hr_user in Odoo 11, this
        method is implemented to retrieve the address_home_id with sudo() for the users who have no
        access to this field in some required scenarios
        """
        return self.sudo().address_home_id

