from odoo.tests.common import SavepointCase


class TestCommon(SavepointCase):

    def setUp(self):
        super(TestCommon, self).setUp()
        self.social_media_1 = self.env['social.media'].create({
            'name': 'Linkedin Media',
            'social_provider': 'linkedin'
        })
        self.social_page_1 = self.env['social.page'].create({
            'name': 'Page Odoo Test',
            'media_id': self.social_media_1.id
        })
        self.social_article_1 = self.env['social.article'].create({
            'name': 'Test',
            'message': 'test',
            'page_ids': [(6, 0, [self.social_page_1.id])],
            'attachment_type': 'file'
        })
        self.attachment_1 = self.env['ir.attachment'].create({
            'name': 'image1 test'
        })
        self.attachment_2 = self.env['ir.attachment'].create({
            'name': 'image2 test'
        })
