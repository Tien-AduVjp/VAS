import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class AccountReportManager(models.Model):
    _name = 'account.report.manager'
    _description = 'manage summary and footnotes of reports'

    report_name = fields.Char(required=True, help='name of the model of the report')
    summary = fields.Char()
    footnotes_ids = fields.One2many('account.report.footnote', 'manager_id')
    company_id = fields.Many2one('res.company')
    financial_report_id = fields.Many2one('account.financial.dynamic.report')

    def add_footnote(self, text, line):
        return self.env['account.report.footnote'].create({'line': line, 'text': text, 'manager_id': self.id})
