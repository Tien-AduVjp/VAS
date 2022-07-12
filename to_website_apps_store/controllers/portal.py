from odoo import _
from odoo.addons.to_odoo_module.controllers import portal
from odoo.exceptions import AccessError
from odoo.http import request


class PortalApp(portal.PortalApp):

    def _odoo_module_version_check_access(self, odoo_module_version_id, access_token=None):
        odoo_module_version = request.env['odoo.module.version'].browse([odoo_module_version_id])
        odoo_module_version_sudo = odoo_module_version.sudo()
        if odoo_module_version.can_download and odoo_module_version_sudo.is_published:
            return odoo_module_version_sudo
        elif odoo_module_version.can_download:
            raise AccessError(_("You don't have permission to access the app %s") % odoo_module_version_sudo.display_name)
        else:
            return super(PortalApp, self)._odoo_module_version_check_access(odoo_module_version_id, access_token)

