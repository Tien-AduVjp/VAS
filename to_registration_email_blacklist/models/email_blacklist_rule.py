# -*- coding: utf-8 -*-

import re

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EmailBlacklistRule(models.Model):
    _name = 'email.blacklist.rule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Blacklisted Email Rules'

    def _default_block_reason(self):
        return self.env.ref('to_registration_email_blacklist.block_reason_common')

    name = fields.Char(string='Blocked Email Rule', required=True, help="The email address that will be blocked during user registration."
                       " You could also use asterisk (*) for wildcard. Here are some examples for your reference,\n"
                       "- company.com: this will block all the registration emails having the domain as 'company.com';\n"
                       "- *.company.com: this will block all the registration emails having the domain as a subdomain of the 'company.com';\n"
                       "- user@company.com: this will block the registration email that exactly matches 'user@company.com';\n"
                       "- *user*@*.company.com: this will block all the registration emails that contain 'user' in their local partner and"
                       " having the domain as a subdomain of the 'company.com';\n"
                       "- company.*: this will block all the registration emails that have the domain prefixed with 'company.' and ended"
                       " with any letters;\n"
                       "- *.company.*: this will block all the registration emails that have '.company.' as a part of their domain name.\n")
    active = fields.Boolean(default=True)
    reason_id = fields.Many2one('block.reason', string='Block Reason', required=True, default=_default_block_reason)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The Blocked Email Rule must be unique!"),
    ]

    def _split_email(self, email):
        """
        Split an email address into two parts of local part (which is prefixed the '@')
        and domain name part (which is suffixed to the '@')
        """
        split = email.split('@')
        domain = split[-1]
        local_part = split[:-1]
        # local_part may contain @, so we join again
        local_part = '@'.join(local_part)
        return local_part, domain

    @api.constrains('name')
    def _check_name(self):
        for r in self:
            local_part, domain = r._split_email(r.name)

            if domain == '*' and (not local_part or local_part == '*'):
                raise UserError(_(
                    "You seemed to want to block any registration. If you really want to do that,"
                    " just disable the customer account Free sign up function instead."))
            if not domain or '.' not in domain:
                raise UserError(_(
                    "You must input the domain name of the email to block. The domain must include at least one dot (.).\n"
                    "You could also use asterisk (*) for wildcard. Here are some examples for your reference,\n"
                    "- company.com: this will block all the registration emails having the domain as 'company.com';\n"
                    "- *.company.com: this will block all the registration emails having the domain as a subdomain of the 'company.com';\n"
                    "- user@company.com: this will block the registration email that exactly matches 'user@company.com';\n"
                    "- *user*@*.company.com: this will block all the registration emails that contain 'user' in their local partner and"
                    " having the domain as a subdomain of the 'company.com';\n"
                    "- company.*: this will block all the registration emails that have the domain prefixed with 'company.' and ended"
                    " with any letters;\n"
                    "- *.company.*: this will block all the registration emails that have '.company.' as a part of their domain name.\n"))

    def is_blacklisted(self, email):
        """
        Check the given email address with all the existing rule and return the matched one if found.
        Otherwise, return and empty rule recordset

        :param email: the given email address to check

        @return: matched rule of empty record rule
        @rtype: email.blacklist.rule record
        """

        def _normalize_to_regex(val):
            val = '\.'.join(val.split('.'))
            val = '.*'.join(val.split('*'))
            return val

        for rule in self.search([]):
            local_part, domain = self._split_email(rule.name)

            if domain:
                domain = _normalize_to_regex(domain)

            if local_part:
                local_part = _normalize_to_regex(local_part)

            regex = '@'.join([local_part, domain]) if local_part else '.*@%s' % domain

            try:
                if re.match(regex, email):
                    return rule
            except Exception as e:
                msg = _(
                    "The email blacklist rule '%s' is invalid during regular expression matching. Here is details:\n%s"
                    ) % (rule.name, e)
                rule.sudo().message_post(body=msg)
                pass

        return self.env['email.blacklist.rule']
