from . import models
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    Rate = env['res.currency.rate']
    rate_ids = Rate.search([])
    if rate_ids:
        rate_ids._compute_inverse_rate()
