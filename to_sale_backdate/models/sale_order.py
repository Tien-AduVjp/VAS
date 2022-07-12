from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        launch_confirmation_wizard = self._context.get('launch_confirmation_wizard', False)
        if launch_confirmation_wizard and self.env.user.has_group('to_backdate.group_backdate'):
            return self.action_confirmation_wizard()
        else:
            res = super(SaleOrder, self).action_confirm()
            date_order = self._context.get('date_order', False)
            if date_order:
                self.write({'date_order': date_order})
            return res

    def action_confirmation_wizard(self):
        self.ensure_one()
        action = self.env.ref('to_sale_backdate.action_wizard_confirm_sale')
        result = action.read()[0]
        # override the context to get rid of the default filtering
        result['context'] = {'default_sale_order_id': self.id}
        result['view_mode'] = 'form'
        res = self.env.ref('to_sale_backdate.wizard_confirm_sale_form_view', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result
