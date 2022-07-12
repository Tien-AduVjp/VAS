from unittest.mock import patch

from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def _prepare_backdate_wizard(self, ctx):
        view = self.env.ref('to_mrp_backdate.mrp_workorder_backdate_wizard_form_view')
        ctx.update({'default_mrp_wo_id': self.id})
        return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mrp.workorder.backdate.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': ctx,
            }

    def button_start(self):
        ctx = dict(self._context or {})
        manual_validate_date_time = ctx.get('manual_validate_date_time', False)
        if ctx.get('open_mrp_workorder_backdate_wizard', False)\
            and not manual_validate_date_time\
            and self.env.user.has_group('to_mrp_backdate.group_mrp_backdate'):
            ctx.update({'default_source_action': 'button_start'})
            return self._prepare_backdate_wizard(ctx)

        if manual_validate_date_time:
            with patch('odoo.addons.mrp.models.mrp_workorder.datetime') as mock_datetime:
                mock_datetime.now.return_value = fields.Datetime.to_datetime(manual_validate_date_time)
                return super(MrpWorkorder, self).button_start()
        return super(MrpWorkorder, self).button_start()

    def button_finish(self):
        ctx = dict(self._context or {})
        manual_validate_date_time = ctx.get('manual_validate_date_time', False)
        if ctx.get('open_mrp_workorder_backdate_wizard', False)\
            and not manual_validate_date_time\
            and self.env.user.has_group('to_mrp_backdate.group_mrp_backdate'):
            ctx.update({'default_source_action': 'button_finish'})
            return self._prepare_backdate_wizard(ctx)

        if manual_validate_date_time:
            with patch('odoo.addons.mrp.models.mrp_workorder.datetime') as mock_datetime:
                mock_datetime.now.return_value = fields.Datetime.to_datetime(manual_validate_date_time)
                return super(MrpWorkorder, self).button_finish()
        return super(MrpWorkorder, self).button_finish()

    def end_previous(self, doall=False):
        """
        @param: doall:  This will close all open time lines on the open work orders when doall = True, otherwise
        only the one of the current user
        """
        # TDE CLEANME
        manual_validate_date_time = self._context.get('manual_validate_date_time', False)
        if manual_validate_date_time:
            backdate = fields.Datetime.to_datetime(manual_validate_date_time)
            with patch('odoo.addons.mrp.models.mrp_workorder.datetime') as mock_datetime:
                with patch('odoo.addons.mrp.models.mrp_workorder.fields.Datetime.now') as mock_fields_datetime_now:
                    mock_datetime.now.return_value = mock_fields_datetime_now.return_value = backdate
                    return super(MrpWorkorder, self).end_previous(doall=doall)
        return super(MrpWorkorder, self).end_previous(doall=doall)

    def button_pending(self):
        ctx = dict(self._context or {})
        manual_validate_date_time = ctx.get('manual_validate_date_time', False)
        if ctx.get('open_mrp_workorder_backdate_wizard', False)\
            and not manual_validate_date_time\
            and self.env.user.has_group('to_mrp_backdate.group_mrp_backdate'):
            ctx.update({'default_source_action': 'button_pending'})
            return self._prepare_backdate_wizard(ctx)
        return super(MrpWorkorder, self).button_pending()

    def button_unblock(self):
        ctx = dict(self._context or {})
        manual_validate_date_time = ctx.get('manual_validate_date_time', False)
        if ctx.get('open_mrp_workorder_backdate_wizard', False)\
            and not manual_validate_date_time\
            and self.env.user.has_group('to_mrp_backdate.group_mrp_backdate')\
            and not len(self) > 1:
            ctx.update({'default_source_action': 'button_unblock'})
            return self._prepare_backdate_wizard(ctx)
        return super(MrpWorkorder, self).button_unblock()
