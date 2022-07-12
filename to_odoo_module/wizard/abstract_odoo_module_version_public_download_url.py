from odoo import models, fields, api


class AbstractOdooModuleVersionPublicDownloadUrl(models.AbstractModel):
    _name = 'abstract.odoo.module.version.public.download.url'
    _description = 'Abstract Odoo Module Version Public Download URL'

    odoo_module_version_id = fields.Many2one('odoo.module.version', string='Odoo Module Version', required=True)
    public_download_url = fields.Char(compute='_compute_public_download_url')

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AbstractOdooModuleVersionPublicDownloadUrl, self).create(vals_list)
        # ensure each odoo module version has valid token
        for omv in records.odoo_module_version_id:
            omv._ensure_rotating_token()
        return records

    @api.depends('odoo_module_version_id')
    def _compute_public_download_url(self):
        # we don't want to have token to get rotated here as we did it in create() already.
        # Rotating token here may give problems with form view onchange as it invalidate cache
        # and cause loosing form data
        for r in self.with_context(do_not_ensure_rotating_token=True):
            r.public_download_url = r.odoo_module_version_id.get_download_url()
