from odoo import models, api, _
from odoo.exceptions import UserError

from . import tools


class IrModule(models.Model):
    _inherit = 'ir.module.module'

    def button_uninstall(self):
        down_dependencies = self.downstream_dependencies()
        to_uninstall_apps = self | down_dependencies
        if 'to_erponline_utility' in to_uninstall_apps.mapped('name'):
            raise UserError(_("Core modules cannot be uninstalled."))
        return super(IrModule, self).button_uninstall()

    def _get_all_to_install_apps(self):
        auto_domain = [('state', '=', 'uninstalled'), ('auto_install', '=', True)]
        install_states = frozenset(('installed', 'to install', 'to upgrade'))

        def must_install(module):
            states = {dep.state for dep in module.dependencies_id}
            return states <= install_states and 'to install' in states

        modules = self
        while modules:
            modules._state_update('to install', ['uninstalled'])
            modules = self.search(auto_domain).filtered(must_install)

        to_install_apps = self.search([('application', '=', True), ('state', 'in', ['to install'])])
        to_install_apps._state_update('uninstalled', ['to install'])
        return to_install_apps

    def button_immediate_install(self):
        # TODOS: check when installing module on list view (remove 'active_id' not in self.env.context)
        if tools.get_saas_subscription_type() == 'user_app' and 'active_id' not in self.env.context and 'skip_warning' not in self.env.context and not tools.get_subscription_is_trial():
            to_install_apps = self._get_all_to_install_apps()
            if to_install_apps:
                action = self.env.ref('to_erponline_utility.install_module_warning_wizard_action').read()[0]
                action['context'] = {
                    'default_module_ids': [(6, 0, to_install_apps.ids)],
                }
                return action
        return super(IrModule, self).button_immediate_install()
