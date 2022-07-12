import logging

from odoo.tools.sql import add_constraint, constraint_definition, drop_constraint
from odoo.addons.link_tracker.models.link_tracker import LinkTracker

from . import controllers
from . import models

_logger = logging.getLogger(__name__)


# TODOs: remove this function on Odoo 15+, because url_utms_uniq constraint is deleted on Odoo 15
def _disable_url_utms_uniq():
    # Remove url_utms_uniq constraint in link.tracker model in link_tracker module
    # It doesn't delete constraint on database server
    # And using @api.constraints instead
    for el in LinkTracker._sql_constraints:
        if el[0] == 'url_utms_uniq':
            _logger.info("Removing the default link tracker's SQL constraint `url_utms_uniq`")
            LinkTracker._sql_constraints.remove(el)
            break


# TODOs: remove this function on Odoo 15+, because url_utms_uniq constraint is deleted on Odoo 15
def post_init_hook(cr, registry):
    if constraint_definition(cr, 'link_tracker', 'link_tracker_url_utms_uniq'):
        drop_constraint(cr, 'link_tracker', 'link_tracker_url_utms_uniq')


# TODOs: remove this function on Odoo 15+, because url_utms_uniq constraint is deleted on Odoo 15
def uninstall_hook(cr, registry):
    add_constraint(cr, 'link_tracker', 'link_tracker_url_utms_uniq', 'unique (url, campaign_id, medium_id, source_id)')


# TODOs: remove this function on Odoo 15+, because url_utms_uniq constraint is deleted on Odoo 15
def post_load():
    _disable_url_utms_uniq()
