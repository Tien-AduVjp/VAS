from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    allow_edit_website_jobs_company_setting = fields.Boolean(string='Allow Website Editors to edit job recruitment pages',
                                                             help="If enabled, the users who are granted as Website Editors will be able " 
                                                             "to edit job recruitment pages on the company's websites.\n"
                                                             "If a job position is set only available for a specific website, "
                                                             "that website is required to have the option "
                                                             "'Allow Website Editors to edit job recruitment pages' enabled too.", default=False)
