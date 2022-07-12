# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('to_product_license.license_version_agpl_v3').write({'short_name': 'AGPL-3'})

