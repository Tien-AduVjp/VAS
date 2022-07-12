from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_company = fields.Boolean(tracking=True)
    name = fields.Char(tracking=True)
    parent_id = fields.Many2one(tracking=True)
    type = fields.Selection(tracking=True)
    street = fields.Char(tracking=True)
    street2 = fields.Char(tracking=True)
    city = fields.Char(tracking=True)
    state_id = fields.Many2one(tracking=True)
    zip = fields.Char(tracking=True)
    country_id = fields.Many2one(tracking=True)
    vat = fields.Char(tracking=True)
    function = fields.Char(tracking=True)
    phone = fields.Char(tracking=True)
    mobile = fields.Char(tracking=True)
    email = fields.Char(tracking=True)
    website = fields.Char(tracking=True)
    category_id = fields.Many2many(tracking=True)
    title = fields.Many2one(tracking=True)
    user_id = fields.Many2one(tracking=True)
    lang = fields.Selection(tracking=True)
    ref = fields.Char(tracking=True)
    industry_id = fields.Many2one(tracking=True)
    comment = fields.Text(tracking=True)
    active = fields.Boolean(tracking=True)
