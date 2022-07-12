from odoo import api, SUPERUSER_ID

from odoo.addons.payment.models.payment_acquirer import create_missing_journal_for_acquirers
from . import controllers
from . import models


def post_init_hook(cr, registry):
    create_missing_journal_for_acquirers(cr, registry)

    env = api.Environment(cr, SUPERUSER_ID, {})
    env['payment.acquirer']._fill_nganluong_supported_currencies()
