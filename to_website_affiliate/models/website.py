from odoo import models, fields

class Website(models.Model):
    _inherit = "website"

    commission_rule_ids = fields.Many2many('affiliate.commission.rule',
                                           string='Websites',
                                           help='The commission rules those are available on this website')
    aff_url_param = fields.Char(string='Affiliate URL Param', default='affcode', required=True,
                                help='The URL param for affiliate. The default value is affcode which will generate'
                                ' affiliate URL like https://viindoo.com/?affcode=xxxxxx')
