# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    block_blacklisted_registration_emails = fields.Boolean(string='Block Blacklisted Registration Emails',
                                                           compute='_compute_block_blacklisted_registration_emails',
                                                           inverse='_set_block_blacklisted_registration_emails',
                                                           help="If enabled, user registration will be constrained by our blacklisted"
                                                           " email rules.")

    def _compute_block_blacklisted_registration_emails(self):
        ConfigParameter = self.env['ir.config_parameter'].sudo()
        block_blacklisted_registration_emails = ConfigParameter.get_param('block_blacklisted_registration_emails')
        for r in self:
            r.block_blacklisted_registration_emails = block_blacklisted_registration_emails

    def _set_block_blacklisted_registration_emails(self):
        block_blacklisted_registration_emails = self and self[0].block_blacklisted_registration_emails or False
        self.env['ir.config_parameter'].sudo().set_param('block_blacklisted_registration_emails', block_blacklisted_registration_emails)
