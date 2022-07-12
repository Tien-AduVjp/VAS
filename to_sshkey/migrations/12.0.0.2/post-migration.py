# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    cr.execute("""
        SELECT id, privkey_bin, pubkey_bin
        FROM sshkey_pair
        """)
    rows = cr.fetchall()

    env = api.Environment(cr, SUPERUSER_ID, {})
    Attachment = env['ir.attachment']

    for row in rows:
        id, privkey_bin, pubkey_bin = row
        privkey_attachment_values = {
            'name': 'privkey_bin',
            'datas': privkey_bin,
            'res_model': 'sshkey.pair',
            'res_field': 'privkey_bin',
            'res_id': id
        }
        pubkey_attachment_values = {
            'name': 'pubkey_bin',
            'datas': pubkey_bin,
            'res_model': 'sshkey.pair',
            'res_field': 'pubkey_bin',
            'res_id': id
        }
        Attachment.create(privkey_attachment_values)
        Attachment.create(pubkey_attachment_values)

    cr.execute("""
        ALTER TABLE sshkey_pair
        DROP COLUMN IF EXISTS privkey_bin,
        DROP COLUMN IF EXISTS pubkey_bin""")
