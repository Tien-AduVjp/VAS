from odoo import models, fields


class WizardOdooModuleVersionPublicDownloads(models.TransientModel):
    _name = 'wizard.odoo.module.version.public.download'
    _inherit = 'abstract.odoo.module.version.public.download.url'
    _description = 'Wizard Odoo Module Version Public Download'

    is_standard_odoo_module = fields.Boolean(related='odoo_module_version_id.is_standard_odoo_module')
