from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['sshkey.pair'].search([])._compute_pubkey_fingerprint()
