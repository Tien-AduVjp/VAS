from . import controllers
from . import models
from . import report

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search([])
    companies._create_helpdesk_team_if_not_exits()
