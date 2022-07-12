from odoo.tests import SavepointCase


class ShortenURLCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(ShortenURLCommon, cls).setUpClass()

        cls.link_greater_60 = 'https://v13demo-vn.erponline.vn/web#action=116&active_id=mailbox_inbox&cids=1&menu_id=90'
        cls.link_greater_60_in_text = "This is demo text https://v13demo-vn.erponline.vn/web#action=116&active_id=mailbox_inbox&cids=1&menu_id=90 This is demo text"
        cls.link_less_than_60 = 'https://v13demo-vn.erponline.vn/web#action=116'
        cls.link_less_than_60_in_text = "This is demo text https://v13demo-vn.erponline.vn/web#action=116 This is demo text"
        cls.shorten_url = cls.env['shorten.url.mixin']
