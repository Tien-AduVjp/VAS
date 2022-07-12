from odoo import api, SUPERUSER_ID
from odoo.tools.sql import constraint_definition, drop_constraint


def _remove_url_utms_uniq(cr):
    # Remove url_utms_uniq constraint in link.tracker model in link_tracker module
    # It delete constraint on database server
    # And using @api.constraints instead
    if constraint_definition(cr, 'link_tracker', 'link_tracker_url_utms_uniq'):
        drop_constraint(cr, 'link_tracker', 'link_tracker_url_utms_uniq')


def migrate(cr, version):
    _remove_url_utms_uniq(cr)
