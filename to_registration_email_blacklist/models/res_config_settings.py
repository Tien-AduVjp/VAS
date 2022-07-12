# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    block_blacklisted_registration_emails = fields.Boolean(related='company_id.block_blacklisted_registration_emails', readonly=False)

    def open_email_blacklist_rule_rules(self):
        action = self.env["ir.actions.act_window"]._for_xml_id('to_registration_email_blacklist.action_email_blacklist_rule')
        return action

    def open_block_reason(self):
        action = self.env["ir.actions.act_window"]._for_xml_id('to_registration_email_blacklist.action_block_reason')
        return action

