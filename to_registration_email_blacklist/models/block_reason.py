# -*- coding: utf-8 -*-

from odoo import models, fields


class BlockReason(models.Model):
    _name = 'block.reason'
    _inherit = 'mail.thread'
    _description = 'Block Reason'

    name = fields.Char(string='Reason', translate=True, required=True, tracking=True)
    solution = fields.Char(string='Solution', translate=True, tracking=True,
                           help="The message that will explain to the users how to solve the registration blocking.")
