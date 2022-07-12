from odoo import http
from odoo.http import request
from odoo.addons.link_tracker.controller.main import LinkTracker
from odoo import SUPERUSER_ID
import werkzeug
AFFCODE_PARAM_NAME = 'to_affiliate_param'


class WebsiteAffiliateLinkTracker(LinkTracker):

    @http.route('/r/<string:code>', type='http', auth='none', website=True)
    def full_url_redirect(self, code, **post):
        link_code = request.env['link.tracker.code'].sudo().search([('code', '=', code)])
        link = link_code.link_id
        res = super(WebsiteAffiliateLinkTracker, self).full_url_redirect(code, **post)
        if link:
            if link.affiliate_code_id:
                affiliate_code = link.affiliate_code_id
                affcode_cookie = request.httprequest.cookies.get(AFFCODE_PARAM_NAME)
                if not affcode_cookie:
                    environ = request.httprequest.headers.environ
                    user = request.env['res.users'].sudo().browse(SUPERUSER_ID)
                    if affiliate_code:
                        UserAgent = werkzeug.useragents.UserAgent(environ.get("HTTP_USER_AGENT"))
                        referrer_data = {
                            'affcode_id': affiliate_code.id,
                            'name': affiliate_code.name,
                            'referrer': environ.get("HTTP_REFERER"),
                            'ip': environ.get("REMOTE_ADDR"),
                            'browser': UserAgent.browser + ' / ' + UserAgent.version
                        }
                        referrer_analysis = request.env['affiliate.referrer'].sudo().create(referrer_data)
                        res.set_cookie('referrer_analysis_id', str(referrer_analysis.id), max_age=user.company_id.affiliate_cookie_age)
                    res.set_cookie(AFFCODE_PARAM_NAME, affiliate_code.name, max_age=user.company_id.affiliate_cookie_age)
        return res
