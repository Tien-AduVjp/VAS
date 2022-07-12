from odoo.tests import tagged

from .shorten_url_common import ShortenURLCommon


@tagged('post_install', '-at_install')
class TestShortenURL(ShortenURLCommon):

    def test_shorten_urls(self):
        """
        Test1: Shorter the link greater 60 characters
        Test2: Shorter the link less than 60 characters
        """
        # Test1
        self.new_link_greater_60 = self.shorten_url.shorten_urls_in_text(self.link_greater_60)
        self.assertNotEqual(self.new_link_greater_60, self.link_greater_60 , "Link is not shortened in spite of long link greater 60")
        
        # Test2
        self.new_link_less_than_60 = self.shorten_url.shorten_urls_in_text(self.link_less_than_60)
        self.assertEqual(self.new_link_less_than_60, self.link_less_than_60 , "Link is shortened in spite of long link less than 60")
    
    def test_shorten_urls_in_text(self):
        """
        Test1: Shorter the link greater 60 characters inside a text
        Test2: Shorter the link less than 60 characters inside a text
        """
        # Test1
        self.new_link_greater_60_in_text = self.shorten_url.shorten_urls_in_text(self.link_greater_60_in_text)
        self.assertNotEqual(self.new_link_greater_60_in_text, self.link_greater_60_in_text , "Inside a text, link is not shortened in spite of long link greater 60")
        
        # Test2
        self.new_link_less_than_60_in_text = self.shorten_url.shorten_urls_in_text(self.link_less_than_60_in_text)
        self.assertEqual(self.new_link_less_than_60_in_text, self.link_less_than_60_in_text , "Inside a text, link is shortened in spite of long link less than 60")
