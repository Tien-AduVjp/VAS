from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    sshkey_pair_ids = fields.One2many('sshkey.pair', 'company_id', string='SSH Keys')
