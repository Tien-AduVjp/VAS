# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    contents = env['website.document.content'].sudo().search([])
    for content in contents:
        content.write({
            'date_published': content.parent_id.date_published,
            'state': content.parent_id.state,
            'validator_id': content.parent_id.validator_id and content.parent_id.validator_id.id or False,
            'website_published': content.parent_id.website_published,
            })

