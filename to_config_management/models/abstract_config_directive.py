from odoo import models, fields


class AbstractConfigDirective(models.AbstractModel):
    _name = 'abstract.config.directive'
    _inherit = 'mail.thread'
    _order = 'name,id'
    _description = 'Share business logics between config models'

    name = fields.Char(string='Key', required=True, tracking=True, index=True)
    value = fields.Char(string='Value', required=True, tracking=True)
    section_id = fields.Many2one('config.section', tracking=True, index=True)
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "The Key of the config directive should not be the description"),
    ]

