from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SoftwareAuthor(models.Model):
    _name = 'software.author'
    _inherit = 'mail.thread'
    _description = 'Software Author'

    name = fields.Char(string='Name', translate=True, required=True, index=True)
    # image: all image fields are base64 encoded and PIL-supported
    image_512 = fields.Binary(related='partner_id.image_512', readonly=True)
    image_256 = fields.Binary(related='partner_id.image_256', readonly=True)
    image_128 = fields.Binary(related='partner_id.image_128', readonly=True)
    partner_id = fields.Many2one('res.partner')
    odoo_module_version_ids = fields.Many2many('odoo.module.version', 'software_author_odoo_module_version_rel', 'author_id', 'module_version_id',
                                          string='Odoo Module Versions', readonly=True)
    odoo_module_versions_count = fields.Integer(string='Module Versions Count', compute='_compute_odoo_module_versions_count')

    @api.depends('odoo_module_version_ids')
    def _compute_odoo_module_versions_count(self):
        for r in self:
            r.odoo_module_versions_count = len(r.odoo_module_version_ids)

    def action_view_odoo_module_versions(self):
        odoo_module_versions = self.mapped('odoo_module_version_ids')
        action = self.env.ref('to_odoo_module.odoo_module_version_action')
        result = action.read()[0]

        # get rid off the default context
        result['context'] = {}

        if len(odoo_module_versions) != 1:
            result['domain'] = "[('author_ids', 'in', " + str(self.ids) + ")]"
        elif len(odoo_module_versions) == 1:
            res = self.env.ref('to_odoo_module.odoo_module_version_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = odoo_module_versions.id
        return result

    def unlink(self):
        for r in self:
            if r.odoo_module_version_ids:
                raise UserError(_("You may not be able to delete author %s while its has an Odoo module version"
                                  " being referred. Please delete all the related Odoo module versions first."))
        return super(SoftwareAuthor, self).unlink()
