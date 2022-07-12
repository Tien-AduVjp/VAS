from . import controllers
from . import models

from odoo import api, SUPERUSER_ID
from odoo.addons.payment.models.payment_acquirer import create_missing_journal_for_acquirers


def post_init_hook(cr, registry):
    create_missing_journal_for_acquirers(cr, registry)

    env = api.Environment(cr, SUPERUSER_ID, {})
    env['payment.acquirer']._fill_vnpay_supported_currencies()
