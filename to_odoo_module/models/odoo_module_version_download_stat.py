from odoo import models, fields


class OdooModuleVersionDownloadStat(models.Model):
    _name = 'odoo.module.version.download.stat'
    _description = 'Odoo Module Version Download Statistics'

    odoo_module_version_id = fields.Many2one('odoo.module.version', string='Odoo Module Version', ondelete='cascade', index=True, required=True)
    odoo_module_id = fields.Many2one(related='odoo_module_version_id.module_id', store=True, index=True)
    product_id = fields.Many2one(related='odoo_module_version_id.product_id', store=True, index=True)
    product_tmpl_id = fields.Many2one(related='product_id.product_tmpl_id', store=True, index=True)
    user_id = fields.Many2one('res.users', string='User', ondelete='cascade', index=True, required=True)
    by_internal_user = fields.Boolean(string='By Internal User', required=True, help="This marks if the download was done by an internal user")
    free_download = fields.Boolean(string='Free Download', required=True, help="This is True when the price is zero"
                                   " AND download is made by an external user")

