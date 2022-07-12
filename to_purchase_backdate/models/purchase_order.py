from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        launch_confirmation_wizard = self._context.get('launch_confirmation_wizard', False)
        if launch_confirmation_wizard and self.env.user.has_group('to_backdate.group_backdate'):
            return self.action_confirmation_wizard()
        else:
            return super(PurchaseOrder, self).button_confirm()

    def button_approve(self, force=False):
        launch_confirmation_wizard = self._context.get('launch_confirmation_wizard', False)
        if launch_confirmation_wizard and self.env.user.has_group('to_backdate.group_backdate'):
            return self.action_confirmation_wizard()
        else:
            res = super(PurchaseOrder, self).button_approve(force)
            date_approve = self._context.get('date_approve', False)
            if date_approve:
                orders = self.filtered(lambda p: p.state in ('purchase', 'done'))
                orders.write({'date_approve': date_approve})
                orders.mapped('order_line').write({'date_order': date_approve})
            return res

    def action_confirmation_wizard(self):
        self.ensure_one()
        action = self.env.ref('to_purchase_backdate.action_wizard_confirm_purchase')
        result = action.read()[0]
        # override the context to get rid of the default filtering
        result['context'] = {'default_purchase_order_id': self.id}
        res = self.env.ref('to_purchase_backdate.wizard_confirm_purchase_form_view', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result
