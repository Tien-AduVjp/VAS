from odoo.tests import SavepointCase


class ToSaleDescShortLinkCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(ToSaleDescShortLinkCommon, cls).setUpClass()
        """Testing with 2 case
            - Link URL standalone
            - Link URL in text"""
        cls.link_url_standalone = 'https://v14demo-vn.viindoo.com/web#action=116&active_id=mailbox_inbox&cids=1&menu_id=90'
        cls.link_url_in_text = "This is demo text https://v14demo-vn.viindoo.com/web#action=116&active_id=mailbox_inbox&cids=1&menu_id=90 This is demo text"
        cls.shorten_url = cls.env['mail.render.mixin']
