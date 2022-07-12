import base64
import requests
from lxml import html

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SocialArticle(models.Model):
    _inherit = 'social.article'

    display_linkedin_preview = fields.Boolean('Display LinkedIn Preview', compute='_compute_display_linkedin_preview')
    linkedin_preview = fields.Html('LinkedIn Preview', compute='_compute_linkedin_preview')

    @api.constrains('page_ids', 'schedule_later')
    def _check_page_ids_and_schedule_later(self):
        for r in self:
            if r.schedule_later:
                for page in r.page_ids:
                    if page.media_id.social_provider == 'linkedin':
                        raise UserError(_("Linkedin does not support post scheduling!"))

    @api.constrains('attachment_ids')
    def _check_update_social_post_linkedin(self):
        for r in self:
            if r.state == 'confirmed':
                for post in r.post_ids:
                    if post.media_id.social_provider == 'linkedin' and post.attachment_ids != r.attachment_ids:
                        raise UserError("You can only update the message of the post on the Linkedin page")

    @api.depends('message', 'page_ids.media_id.social_provider')
    def _compute_display_linkedin_preview(self):
        for r in self:
            r.display_linkedin_preview = (
                r.message and
                'linkedin' in r.page_ids.media_id.mapped('social_provider'))

    @api.depends('message', 'attachment_ids', 'attachment_link', 'attachment_type', 'display_linkedin_preview')
    def _compute_linkedin_preview(self):
        for r in self:
            if r.display_linkedin_preview:
                data_dict = {
                    'message': r.message,
                    'published_date': fields.Datetime.now()
                }
                if r.attachment_type == 'none' and r.attachment_link:
                    res = requests.get(r.attachment_link)
                    self.raise_http_error(res, r.attachment_link)
                    data = html.fromstring(res.text.encode('utf-8'), parser=html.HTMLParser(encoding='utf-8'))
                    if data:
                        data_dict.update({
                            'title': data.xpath("//meta[@property='og:title']")[0].attrib.get('content', False) if data.xpath("//meta[@property='og:title']") else r.attachment_link_title,
                            'description': data.xpath("//meta[@property='og:description']")[0].attrib.get('content', '') if data.xpath("//meta[@property='og:description']") else '',
                            'site_name': r.attachment_link.split("//")[1].split("/")[0],
                            'image_url': data.xpath("//meta[@property='og:image']")[0].attrib.get('content', False) if data.xpath("//meta[@property='og:image']") else False
                        })
                elif r.attachment_type == 'file' and r.attachment_ids:
                    attachments = r.attachment_ids.sorted('id') if r.attachment_ids == r.attachment_ids._origin else r.attachment_ids
                    data_dict.update({
                        'images': [
                            image.datas if not image.id
                            else base64.b64encode(open(image._full_path(image.store_fname), 'rb').read()) for image in attachments
                        ]
                    })
                r.linkedin_preview = self.env.ref('viin_social_linkedin.linkedin_preview')._render(data_dict)
            else: r.linkedin_preview = False

    def action_confirm(self):
        self.ensure_one()
        if self.attachment_type == 'file' and 'linkedin' in self.media_ids.mapped('social_provider'):
            is_check_file = is_image = is_video = file_size = False
            for file in self.attachment_ids:
                if file.mimetype in ['image/png', 'image/jpeg']:
                    is_image = True
                    is_check_file = True
                if file.mimetype == 'video/mp4':
                    if is_video:
                        raise UserError(_("LinkedIn Page: You cannot post multiple videos on Linkedin"))
                    is_video = True
                    file_size = file.file_size
                    is_check_file = True
            if not is_check_file:
                raise UserError(_("LinkedIn Page: You need to choose the right file format: *png, *jpeg, *mp4"))

            if is_image and is_video:
                raise UserError(_("LinkedIn Page: You cannot post both photos and videos to Linkedin"))
            if is_video and file_size > 200000000: # ~200MB
                raise UserError(_("LinkedIn Page: Please select video with size <200Mb"))
        return super(SocialArticle, self).action_confirm()
