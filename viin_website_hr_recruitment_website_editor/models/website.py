from odoo import models, fields

class Website(models.Model):
    _inherit = 'website'

    allow_edit_website_jobs_website_setting = fields.Boolean(string='Allow Website Editors to edit this website\'s job recruitment pages',
                                                             help="If enabled, the users who are granted as Website Editors will be able to "
                                                             "edit job recruitment pages on the current websites as long as the company allows that.\n"
                                                             "This option does not affect job positions that have no website set. "
                                                             "Those job positions are constrained by the corresponding company's settings.", default=False)
