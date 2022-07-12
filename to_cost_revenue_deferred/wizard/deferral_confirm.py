from odoo import fields, models, _


class DeferralConfirm(models.TransientModel):
    _name = 'deferral.confirm'
    _description = 'Cost / Revenue Deferral Confirm'

    date = fields.Date('Account Date', required=True, default=fields.Date.context_today,
                       help="Choose the period for which you want to automatically post the deferral lines of running deferral")

    def deferral_compute(self):
        self.ensure_one()
        created_move_ids = self.env['cost.revenue.deferral'].compute_generated_entries(self.date)

        return {
            'name': _('Created Cost / Revenue Deferral Moves'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'domain': [('id','in', created_move_ids)],
            'type': 'ir.actions.act_window',
        }
