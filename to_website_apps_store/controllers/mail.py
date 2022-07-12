from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import mail

class PortalChatter(mail.PortalChatter):

    @http.route(['/mail/chatter_post'], type='http', methods=['POST'], auth='public', website=True)
    def portal_chatter_post(self, res_model, res_id, message, **kw):
        # override to not allow a user to rate a module if she or he did not buy it.
        if res_model == 'odoo.module.version' and res_id:
            odoo_module_version = request.env[res_model].browse(int(res_id))
            if 'rating_value' in kw and kw.get('rating_value') != '0.0' and not odoo_module_version.can_download:
                return request.render('to_website_apps_store.unauthorized_rating')
            # portal users need access token to rating apps
            kw.update(token=odoo_module_version.access_token)
        return super(PortalChatter, self).portal_chatter_post(res_model, res_id, message, **kw)
