from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_edit_website_jobs_website_setting = fields.Boolean(related='website_id.allow_edit_website_jobs_website_setting', readonly=False)
    allow_edit_website_jobs_company_setting = fields.Boolean(related='company_id.allow_edit_website_jobs_company_setting', readonly=False)
