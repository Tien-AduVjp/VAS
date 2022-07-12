import logging
_logger = logging.getLogger(__name__)

try:
    from validators.url import url as is_valid_url
except ImportError as e:
    _logger.error("Could NOT do 'import validators'. Please install validators by firing command 'pip install validators'")

from odoo import models, api


class ShortenURL(models.AbstractModel):
    _name = 'shorten.url.mixin'
    _description = "Shorten URL Mixin"

    @api.model
    def shorten_urls(self, urls, utm_source=None, campaign=None, medium=None):
        """
        Method to shorted given URLs
        
        :param urls: single URL in type of string or a list of URLs (each is
        :param utm_source: utm.source record or None
        :param campaign: utm.campaign record or None
        :param medium: utm.medium record or None
        
        @return: link.traker recordset that contains shorted URLs for the given urls
        """
        if isinstance(urls, str):
            urls = [urls]

        vals_list = []
        for url in urls:
            vals = {
                'url': url  # target URL
                }
            if utm_source:
                vals['source_id'] = utm_source.id
            if campaign:
                vals['campaign_id'] = campaign.id
            if medium:
                vals['medium_id'] = medium.id
            vals_list.append(vals)
        return self.env['link.tracker'].sudo().create(vals_list)

    @api.model
    def shorten_urls_in_text(self, text, utm_source=None, campaign=None, medium=None, max_lenth=60):
        """
        Method to shorted given URLs inside a text
        
        :param text: a given text that may contain URLs for shortening
        :param utm_source: utm.source record or None
        :param campaign: utm.campaign record or None
        :param medium: utm.medium record or None
        :param max_lenth: the max length of the URL for shortening triggered
        
        @return: new text that contains shorten URLs for the original URLs that are longer than the max_length
        """
        lines_split = text.split('\n')
        for lidx, line in enumerate(lines_split):
            word_split = line.split()
            for idx, split in enumerate(word_split):
                if is_valid_url(split) and len(split) > max_lenth:
                    link_tracker = self.shorten_urls(split, utm_source, campaign, medium)
                    if link_tracker:
                        word_split[idx] = link_tracker.short_url
            lines_split[lidx] = " ".join(word_split)
        return '\n'.join(lines_split)
