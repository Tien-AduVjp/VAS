from odoo import models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        manual_validate_date_time = self._context.get('manual_validate_date_time')
        if self._context.get('open_mrp_markdone_backdate_wizard', False)\
            and not manual_validate_date_time\
            and self.env.user.has_group('to_mrp_backdate.group_mrp_backdate'):
            view = self.env.ref('to_mrp_backdate.mrp_markdone_backdate_wizard_form_view')
            ctx = dict(self._context or {})
            ctx.update({'default_mrp_order_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mrp.markdone.backdate.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': ctx,
            }
        res = super(MrpProduction, self).button_mark_done()
        if manual_validate_date_time:
            orders = self.filtered(lambda o: o.state == 'done')
            if orders:
                orders.write({'date_finished': manual_validate_date_time})
        return res
