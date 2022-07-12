import logging

from odoo import api
from odoo.models import AbstractModel
from odoo.tools import config

_logger = logging.getLogger(__name__)

config['publisher_warranty_url'] = ''


class PublisherWarrantyContract(AbstractModel):
    _inherit = 'publisher_warranty.contract'

    def update_notification(self, cron_mode=True):
        _logger.info("NO More Spying Stuff")
        return True

