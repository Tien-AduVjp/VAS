from odoo import models, fields, api


class WizardGitURLAdd(models.TransientModel):
    _inherit = 'wizard.git.url.add'

    auto_module_discovery = fields.Boolean(string='Auto Modules Discovery',
                                           compute='_get_auto_module_discovery', inverse='_set_auto_module_discovery', store=True,
                                           help="If enabled, scanning this branch will discover Odoo modules in the branch automatically.")

    generate_app_products = fields.Boolean(string='Generate App Products',
                                           compute='_get_generate_app_products', inverse='_set_generate_app_products', store=True,
                                           help="If checked, discovering Odoo modules from this"
                                           " branch will also generate app products repectively.\n"
                                           "Note: no matter this field is enabled or not, app products will NOT be generated if this branch"
                                           " contains either Odoo CE code base or Odoo Enterprise code base")

    @api.depends('checkout')
    def _get_auto_module_discovery(self):
        for r in self:
            r.auto_module_discovery = r.checkout

    def _set_auto_module_discovery(self):
        pass

    @api.depends('checkout', 'auto_module_discovery')
    def _get_generate_app_products(self):
        for r in self:
            r.generate_app_products = r.checkout and r.auto_module_discovery

    def  _set_generate_app_products(self):
        pass

    def _prepare_git_branch_data(self, repository):
        vals = super(WizardGitURLAdd, self)._prepare_git_branch_data(repository)
        vals.update({
            'auto_module_discovery': self.auto_module_discovery,
            'generate_app_products': self.generate_app_products
            })
        return vals

    def add(self):
        self.ensure_one()
        branch = super(WizardGitURLAdd, self).add()
        if self.auto_module_discovery:
            branch.with_context(
                ignore_error=self._context.get('ignore_auto_module_discovery_error', False)
                ).action_pull()
        return branch

