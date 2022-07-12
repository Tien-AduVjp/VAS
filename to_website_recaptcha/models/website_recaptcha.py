from odoo import api, models


class WebsiteRecaptcha(models.AbstractModel):

    _name = 'website.recaptcha'
    _description = 'Website Recaptcha Validations'

    @api.model
    def validate_request(self):
        return self.env['ir.http']._verify_request_recaptcha_token('website_recaptcha')
