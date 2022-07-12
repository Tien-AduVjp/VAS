import base64

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError
from odoo.http import request, content_disposition
from odoo.tools import consteq


class PortalApp(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super(PortalApp, self)._prepare_home_portal_values(counters)
        if 'apps_count' in counters:
            partner = request.env.user.partner_id
            odoo_module_versions = partner.get_paid_odoo_apps(use_commercial_partner=True)[0]
            apps_count = len(odoo_module_versions)
            values.update({
                'apps_count': apps_count,
            })
        return values

    @http.route(['/my/apps', '/my/apps/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_apps(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        odoo_module_versions = partner.get_paid_odoo_apps(use_commercial_partner=True)[0]

        values.update({
            'odoo_apps': odoo_module_versions.with_context(filtered_user=request.env.user),
            'page_name': 'Odoo Apps',
            'default_url': '/my/apps',
        })
        return request.render("to_odoo_module.portal_my_apps", values)

    def _odoo_module_version_check_access(self, odoo_module_version_id, access_token=None):
        user = request.env.user
        odoo_module_version = request.env['odoo.module.version'].browse([odoo_module_version_id])
        odoo_module_version_sudo = odoo_module_version.sudo()
        if user.has_group('to_odoo_module.odoo_module_user') or (access_token and consteq(odoo_module_version_sudo.access_token, access_token)) or odoo_module_version.can_download:
            return odoo_module_version_sudo
        else:
            raise AccessError(_("You don't have permission to access the app %s") % odoo_module_version_sudo.display_name)

    @http.route(['/my/apps/download/<int:odoo_module_version_id>'], type='http', auth="public", website=True)
    def portal_my_apps_download(self, odoo_module_version_id, access_token=None, **kw):
        try:
            odoo_module_version_sudo = self._odoo_module_version_check_access(odoo_module_version_id, access_token)
        except AccessError:
            return request.redirect('/my')

        wizard = request.env['wizard.odoo.module.version.download'].with_context(active_test=False).sudo().create({
            'module_ids': [(4, odoo_module_version_id)]
            })
        wizard.zip_dirs()
        if not wizard.zip_all:
            return request.redirect('/my')
        filecontent = base64.b64decode(wizard.zip_all)
        odoo_module_version_sudo.with_context(download_user=request.env.user).increase_download_count()

        ziphttpheaders = [
            ('Content-Type', 'application/zip'),
            ('Content-Length', len(filecontent)),
            ('Content-Disposition', content_disposition(wizard.zip_all_filename))
        ]
        return request.make_response(filecontent, headers=ziphttpheaders)

    @http.route(['/apps/<string:odoo_version_name>/<string:technical_name>/static/description/<string:image_name>'],
                type='http', auth="public", website=True)
    def view_app_image(self, odoo_version_name, technical_name, image_name, **kw):
        """
        Trigger URL in form of /apps/10.0/to_fleet_accounting/static/description/fleet_accounting_preview.png
        """
        odoo_module_version = request.env['odoo.module.version'].sudo().search([
            ('odoo_version_id.name', '=', odoo_version_name),
            ('technical_name', '=', technical_name),
            ], limit=1)
        return odoo_module_version.read_resource(image_name)

