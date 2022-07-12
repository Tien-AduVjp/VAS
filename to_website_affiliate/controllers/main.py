import datetime
import werkzeug

from odoo import http, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo import SUPERUSER_ID

from odoo.addons.website.controllers.main import Website

from odoo.addons.website_sale.controllers.main import WebsiteSale

AFFCODE_PARAM_NAME = 'to_affiliate_param'


class WebsiteAffiliateRegister(http.Controller):

    @http.route(['/affiliate', '/affiliate/<model("res.users"):user>'], type='http', auth="user", website=True, sitemap=False)
    def affiliate_register(self, user=None, **kwargs):
        res_company = request.env['res.company'].sudo().search([], limit=1)
        medium = request.env['utm.medium'].sudo().search([('active', '=', True), ('available_for_affiliate_portal', '=', True)])
        source = request.env['utm.source'].sudo().search([('available_for_affiliate_portal', '=', True)])
        values = {}
        aff_code = False
        user = request.env.user
        if user and user.partner_id.is_affiliate:
            aff_code = request.env['affiliate.code'].sudo().search([('partner_id', '=', user.partner_id.id)], limit=1)
            links = request.env['link.tracker'].sudo().search([('affiliate_code_id.name', '=', aff_code.name)])
            values.update(kwargs={'res_company': res_company, 'user': user, 'aff_code': aff_code})
            values['medium'] = medium
            values['source'] = source
            values['links'] = links
            return request.render("to_website_affiliate.to_affiliate", values)
        else:
            return werkzeug.utils.redirect('/affiliate/join')

    @http.route(['/affiliate/commissions'], type='http', auth="user", website=True, sitemap=False)
    def affiliate_comissions(self, **kwargs):
        user = request.env.user
        comissions = None
        values = {}
        if user and user.partner_id.is_affiliate:
            affiliate_code = request.env['affiliate.code'].sudo().search([('partner_id.id', '=', user.partner_id.id)])
            comissions = request.env['affiliate.commission'].sudo().search([('partner_id.id', '=', affiliate_code.partner_id.id), ('state', '=', 'confirm')])
            values['comissions'] = comissions
        return request.render("to_website_affiliate.to_affiliate_commissions", values)

    @http.route(['/affiliate/payment_requests', '/affiliate/payment_requests/<int:request_id>'], type='http', auth="user", website=True, sitemap=False)
    def affiliate_payment_requests(self, request_id=None, **kwargs):
        user = request.env.user
        values = {}
        requests = None
        if user and user.partner_id.is_affiliate:
            if request_id:
                pay_request = request.env['affiliate.payment'].sudo().search([('id', '=', request_id)])
                values['total'] = pay_request.total
                values['today'] = pay_request.date
                values['min_payout'] = request.website.company_id.affiliate_min_payout
                values['commissions'] = pay_request.com_ids
                values['pay_request'] = pay_request
                return request.render("to_website_affiliate.to_affiliate_payment_request_detail", values)

            affiliate_code = request.env['affiliate.code'].sudo().search([('partner_id.id', '=', user.partner_id.id)])
            commissions = request.env['affiliate.commission'].sudo().search([
                ('partner_id.id', '=', affiliate_code.partner_id.id),
                ('state', '=', 'confirm')
            ])

            requests = request.env['affiliate.payment'].sudo().search([('partner_id.id', '=', user.partner_id.id)])
            values['total'] = commissions._get_commission_amount(date=datetime.date.today())
            values['min_payout'] = request.website.company_id.affiliate_min_payout
            values['requests'] = requests
        return request.render("to_website_affiliate.to_affiliate_payment_requests", values)

    @http.route(['/affiliate/payment_requests/new'], type='http', auth="user", website=True, sitemap=False)
    def affiliate_new_payment_requests(self, **kwargs):
        user = request.env.user
        values = {}
        if user and user.partner_id.is_affiliate:
            affiliate_code = request.env['affiliate.code'].sudo().search([('partner_id.id', '=', user.partner_id.id)])
            commissions = request.env['affiliate.commission'].sudo().search([
                    ('partner_id.id', '=', affiliate_code.partner_id.id),
                    ('state', '=', 'confirm')
                ])

            if request.httprequest.method == 'POST':
                notes = kwargs.get('notes', '')
                nrequest = request.env['affiliate.payment'].sudo().create({
                        'notes': notes,
                        'partner_id': user.partner_id.id,
                        'date': datetime.datetime.now(),
                        'total': commissions._get_commission_amount(date=datetime.date.today())
                    })
                if nrequest:
                    nrequest.action_confirm()
                    return werkzeug.utils.redirect('/affiliate/payment_requests/' + str(nrequest.id))

            values['total'] = commissions._get_commission_amount(date=datetime.date.today())
            values['today'] = datetime.datetime.now().strftime('%Y-%m-%d')
            values['min_payout'] = request.website.company_id.affiliate_min_payout
            values['commissions'] = commissions
        return request.render("to_website_affiliate.to_affiliate_payment_request_detail", values)

    @http.route(['/affiliate/invoices', '/affiliate/invoices/page/<int:page>'], type='http', auth="user", website=True, sitemap=False)
    def portal_my_invoices(self, page=1, date_begin=None, date_end=None, **kw):
        values = {
            'company': request.website.company_id,
            'user': request.env.user
        }
        partner = request.env.user.partner_id
        AccountMove = request.env['account.move']

        domain = [
            ('move_type', 'in', ['in_invoice', 'in_refund']),
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('aff_payment_ids', '!=', False)
        ]
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        invoice_count = AccountMove.search_count(domain)
        # pager
        pager = request.website.pager(
            url="/affiliate/invoices",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=invoice_count,
            page=page,
            step=20
        )
        # content according to pager and archive selected
        invoices = AccountMove.search(domain, limit=20, offset=pager['offset'])
        values.update({
            'date': date_begin,
            'invoices': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'default_url': '/affiliate/invoices',
        })
        return request.render("to_website_affiliate.portal_affiliate_invoices", values)

    @http.route(['/affiliate/update_link/<int:link_id>'], type='http', auth='user', methods=['POST'], website=True)
    def to_website_update_link(self, link_id, **kwargs):
        link = request.env['link.tracker'].browse(link_id).exists().sudo()
        if link.create_uid != request.env.user:
            return werkzeug.exceptions.Forbidden()

        link.write({
            'title': kwargs['new_name'],
            'medium_id': int(kwargs['new_medium']),
            'source_id': int(kwargs['new_source'])
        })
        return '1'

    @http.route(['/affiliate/remove_link/<int:link_id>'], type='http', auth='user', methods=['POST'], website=True)
    def to_website_remove_link(self, link_id, **kwargs):
        link = request.env['link.tracker'].browse(link_id).exists().sudo()
        if link.create_uid != request.env.user:
            return werkzeug.exceptions.Forbidden()

        update = link.unlink()
        return '1' if update else '0'

    @http.route(['/affiliate/create_link'], type='http', auth="public", website=True, sitemap=False)
    def to_website_add_link(self, **kwargs):
        user = request.env.user
        new_link_tracker = None
        if user and user.partner_id.is_affiliate:
            affiliate_code = request.env['affiliate.code'].sudo().search([('partner_id.id', '=', user.partner_id.id)])
            link_title = kwargs.get('title', False)
            link_url = kwargs.get('url', '')
            medium = kwargs.get('medium', False)
            source = kwargs.get('source', False)

            base_url = request.website.get_base_url()
            if not link_url.startswith(base_url):
                raise UserError(_("Target URL must start with %s.") % base_url)

            if link_title and link_url:
                new_link_tracker = request.env['link.tracker'].sudo().create({
                    'title': link_title,
                    'url': link_url,
                    'medium_id': int(medium),
                    'source_id': int(source),
                    'affiliate_code_id': affiliate_code.id
                })
        return werkzeug.utils.redirect('/affiliate')

    @http.route(['/affiliate/join'], type='http', auth="user", website=True, sitemap=False)
    def join_affiliate(self, **kwargs):

        env = request.env(user=SUPERUSER_ID)
        user_id = request.env.user.id
        # company_id = kwargs.get('res_company', False)
        company_id = request.website.company_id.id
        super_user = env['res.users'].browse(SUPERUSER_ID)
        if not company_id or int(company_id) == 0:
            company_id = super_user.company_id.affcode_default_company.id
        if user_id:
            user = env['res.users'].browse(int(user_id))
            if not user.partner_id.is_affiliate:
                aff_code = env['affiliate.code'].sudo().create({
                    'partner_id': user.partner_id.id,
                    'company_id': company_id,
                    'website_id': request.website and request.website.id or False
                })
            return request.redirect('/affiliate/%s' % user_id, code=302)
        return request.redirect('/affiliate', code=302)


class Website(Website):

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        res = super(Website, self).index(**kw)
        affcode = kw.get(AFFCODE_PARAM_NAME, False)
        if affcode:
            affcode_cookie = request.httprequest.cookies.get(AFFCODE_PARAM_NAME)
            if not affcode_cookie:

                environ = request.httprequest.headers.environ
                user = request.env['res.users'].sudo().browse(SUPERUSER_ID)
                affiliate_code = request.env['affiliate.code'].sudo().search([('name', '=', affcode)], limit=1)
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
                res.set_cookie(AFFCODE_PARAM_NAME, affcode, max_age=user.company_id.affiliate_cookie_age)
        return res


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        value = super(WebsiteSale, self).confirm_order(**post)
        sale_order_id = request.session.get('sale_last_order_id')
        affcode_cookie = request.httprequest.cookies.get(AFFCODE_PARAM_NAME)
        referrer_analysis_id = request.httprequest.cookies.get('referrer_analysis_id')
        if sale_order_id:
            env = request.env(user=SUPERUSER_ID)
            sale_order = env['sale.order'].browse(sale_order_id)
            if affcode_cookie:
                affcode = env['affiliate.code'].search([('name', '=', affcode_cookie)], limit=1)
                if affcode:
                    affcodes = env['affiliate.code'].search([])
                    sale_orders = env['sale.order'].search([
                                                            ('affcode_id', 'in', [x.id for x in affcodes]),
                                                            ('partner_id', '=', sale_order.partner_id.id),
                                                            ('state', 'not in', ['draft', 'sent', 'cancel'])
                                                            ]
                                                           )
                    if not sale_orders:
                        sale_order.write({
                            'affcode_id': affcode.id,
                            'user_id': affcode.salesperson_id.id,
                            'referrer_analysis_id': referrer_analysis_id and int(referrer_analysis_id) or False
                        })

        return value

    def checkout_parse(self, address_type, data, remove_prefix=False):
        values = super(WebsiteSale, self).checkout_parse(address_type, data, remove_prefix=remove_prefix)
        affcode_cookie = request.httprequest.cookies.get(AFFCODE_PARAM_NAME)
        if affcode_cookie:
            env = request.env(user=SUPERUSER_ID)
            affcode = env['affiliate.code'].search([('name', '=', affcode_cookie)], limit=1)
            if affcode:
                values.update({'affcode_id': affcode.id})
        return values
