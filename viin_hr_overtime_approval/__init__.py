from . import models
from . import report
from . import wizard

from odoo import api, SUPERUSER_ID, _


def _generate_approval_request_type(env):
    companies = env['res.company'].with_context(active_test=False).search([])
    if companies:
        companies._generate_approval_request_type()

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _generate_approval_request_type(env)
