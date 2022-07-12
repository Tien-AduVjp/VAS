from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class AssetRevaluationWizard(models.TransientModel):
    _name = 'asset.revaluation.wizard'
    _description = 'Revaluation Wizard of Asset'
    
    
    name = fields.Text(string='Reason', required=True)
    revaluation_date = fields.Date(string='Date of Revaluation', required=True, default=lambda self: fields.Date.context_today(self))
    method = fields.Selection([('decrease', 'Decrease'), ('increase', 'Increase')], string='Method', default='decrease', required=True)
    value = fields.Float(string='Value', digits=0, required=True)
    
    def button_revaluation(self):
        """ Revaluation of asset."""
        asset_id = self._context.get('active_id', False)
        asset = self.env['account.asset.asset'].browse(asset_id)
        
        if float_compare(self.value, 0.0, precision_digits=asset.currency_id.decimal_places) != 1:
            raise UserError(_('Revaluation Value must be greater than 0.'))
        
        first_depreciation_date = asset.date_first_depreciation == 'manual' and asset.first_depreciation_date or asset.date
        if self.revaluation_date < first_depreciation_date:
            raise UserError(_('Date of Revaluation must be greater than Date or First Depreciation Date of Asset.'))
        
        if self.method =='decrease' and self.value > asset.value_residual:
            raise UserError(_('Revaluation Value must be lesser than Residual Value of Asset.'))
        
        revaluation_line_obj = self.env['account.asset.revaluation.line']
        vals = revaluation_line_obj._prepare_revaluation_line_vals(asset, self.name, self.value, self.method, self.revaluation_date)
        revaluation_line_obj.create(vals)
        return {'type': 'ir.actions.act_window_close'}
