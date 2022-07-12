from odoo import models, fields, api


class AccountReportMulticompanyManager(models.TransientModel):
    _name = 'account.report.multicompany.manager'
    _description = 'Manages Multi-company for Reports'

    @api.model
    def _default_company_ids(self):
        companies = self.env['res.company']
        for journal in self.env['account.journal'].search([]):
            companies |= journal.company_id
        return companies

    multi_company = fields.Boolean('Allow multi-company', compute='_get_multi_company', store=False)
    company_ids = fields.Many2many('res.company', relation='account_report_context_company', string='Companies', default=lambda s: s._default_company_ids())
    available_company_ids = fields.Many2many('res.company', relation='account_report_context_available_company', string='Available companies', default=lambda s: s._default_company_ids())

    def _get_multi_company(self):
        group_multi_company = self.env['ir.model.data'].xmlid_to_object('base.group_multi_company')
        for r in self:
            if r.create_uid.id in group_multi_company.users.ids:
                r.multi_company = True
            else:
                r.multi_company = False

    def get_available_company_ids_and_names(self):
        return [[c.id, c.name] for c in self.available_company_ids]

    @api.model
    def get_available_companies(self):
        return self.env.user.company_ids
