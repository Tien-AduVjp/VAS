# -*- coding: utf-8 -*-
from odoo import api, fields, SUPERUSER_ID


def migrate(cr, version):
     # update data for paperformat
    env = api.Environment(cr, SUPERUSER_ID, {})
    paperformat = env.ref('to_l10n_vn_qweb_layout.to_qwl_template_paperformat_portrait', raise_if_not_found=False)
    if paperformat:
        paperformat.write({'margin_top' : 35, 'header_spacing': 30})
