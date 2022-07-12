# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountReportFootnote(models.Model):
    _name = "account.report.footnote"
    _description = "Footnote for reports"

    text = fields.Char()
    line = fields.Char(index=True)
    manager_id = fields.Many2one('account.report.manager')

