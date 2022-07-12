from unittest.mock import patch

from odoo.tests.common import tagged
from odoo.exceptions import UserError
from odoo.addons.base.models.ir_attachment import IrAttachment

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestSocialArticle(TestCommon):
    
    @patch.object(IrAttachment, 'write', lambda self, vals: super(IrAttachment, self).write(vals))
    def test_action_confirm(self):
        # case 1:
        self.social_article_1.attachment_type = 'none'
        self.social_article_1.action_confirm()
        
        # case 2:
        self.social_article_1.write({
            'attachment_ids': [(6, 0, [self.attachment_1.id])],
            'attachment_type': 'file'
        })
        self.attachment_1.mimetype = 'text/plain'
        with self.assertRaises(UserError):
            self.social_article_1.action_confirm()
        
        # case 3:
        self.attachment_1.mimetype = 'video/mp4'
        self.attachment_2.mimetype = 'video/mp4'
        self.social_article_1.attachment_ids = self.attachment_1 + self.attachment_2
        
        with self.assertRaises(UserError):
            self.social_article_1.action_confirm()
        
        # case 4:
        self.attachment_1.mimetype = 'video/mp4'
        self.attachment_2.mimetype = 'image/png'
        self.social_article_1.attachment_ids = self.attachment_1 + self.attachment_2
        
        with self.assertRaises(UserError):
            self.social_article_1.action_confirm()
        
        # case 5:
        self.social_article_1.attachment_ids = self.attachment_1
        self.attachment_1.file_size = 201 * 1024 * 1024
        with self.assertRaises(UserError):
            self.social_article_1.action_confirm()
        
    def test_02_action_confirm(self):
         # case 6:
        self.attachment_1.mimetype = 'image/png'
        self.social_article_1.attachment_ids = self.attachment_1
        self.social_article_1.action_confirm()
        
        # case 7:
        self.attachment_2.mimetype = 'image/png'
        self.social_article_1.attachment_ids = self.attachment_1 + self.attachment_2
        self.social_article_1.action_confirm()
