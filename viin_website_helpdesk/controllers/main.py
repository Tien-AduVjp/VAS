from werkzeug.exceptions import NotFound, Forbidden

from odoo import _, http
from odoo.http import request
from odoo.addons.viin_helpdesk.controllers import portal


class WebsiteHelpdesk(http.Controller):
    
    @http.route(['/ticket',
                 '/ticket/team',
                 '/ticket/team/<int:tid>'], auth='public', type='http', website=True, sitemap=False)
    def _websie_helpdesk_team(self, tid=False, **kw):
        HelpdeskTeam = request.env['helpdesk.team'].sudo()
        is_helpdesk_manager = request.env.user.has_group('viin_helpdesk.group_helpdesk_manager')
        if tid:
            team = HelpdeskTeam.search([('id', '=', tid)])
            if team and not team.website_published and not is_helpdesk_manager:
                raise Forbidden
            elif not team:
                raise NotFound
            return request.render('viin_website_helpdesk.website_helpdesk_team_details', {
                'team': team,
                'main_object': team
            })
        else:
            if not is_helpdesk_manager:
                teams = HelpdeskTeam.search([('website_published','=',True)])
            else:
                teams = HelpdeskTeam.search([])
            return request.render('viin_website_helpdesk.website_helpdesk_team_index', {
                'teams': teams,
            })

    @http.route(['/ticket/create',
                 '/ticket/create/<int:tid>'], type='http', auth='public', methods=['GET', 'POST'], website=True, csrf=True, sitemap=False)
    def _create_new_helpdesk(self, tid=None, **post):
        data = {
            'tid': tid
            }
        error = False
        
        HelpdeskTeam = request.env['helpdesk.team'].sudo()
        if post and request.httprequest.method == 'POST':
            # Validate form's captcha
            Recaptcha = request.env['website.recaptcha'].sudo()
            validated = Recaptcha.validate_request(request, post)
            email_from = post.get('email_from', False)
            if validated:
                if email_from:
                    vals = portal._prepare_ticket_vals(request.env, **post)
                    # Get support team
                    team_id = post.get('team_id', 0)
                    if team_id:
                        tid = team_id
                    data['team'] = HelpdeskTeam.search([('id','=',tid),('website_published','=',True)])

                    vals.update({
                        'contact_name': post.get('contact_name', ''),
                        'email_from': email_from
                        })
                    ticket = request.env['helpdesk.ticket'].sudo().create(vals)
                    ticket.flush()
                    # Send ticket email
                    mail_template = request.env.ref('viin_website_helpdesk.mail_template_partner_helpdesk_ticket_created', raise_if_not_found=False)
                    if mail_template:
                        share_url = ticket._get_share_url()
                        mail_template.sudo().with_context(
                            lang=request.env.user.partner_id.lang or 'en_US',
                            share_url=share_url,
                        ).send_mail(ticket.id, force_send=True)
                    return request.render('viin_website_helpdesk.website_helpdesk_create_success', data)
                else:
                    error = _("Please enter valid email.")
            else:
                error = _("Please check the recaptcha.")
        
        if error:
            data['error'] = error
        # Generate create form
        if request.env.user != request.env.ref('base.public_user', raise_if_not_found=False):
            data['user'] = request.env.user
        data['teams'] = HelpdeskTeam.search([('website_published','=',True)])
        return request.render('viin_website_helpdesk.website_helpdesk_create_form', data)
    
    