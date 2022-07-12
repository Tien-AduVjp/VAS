from odoo import models, fields, api


class ActionConfirmWizard(models.TransientModel):
    _name = 'action.confirm.wizard'
    _description = "Action Confirm Wizard"
    
    warranty_claim_id = fields.Many2one('warranty.claim', string='Warranty Claim')
    
    def write_state_to_confirm(self):
        return self.warranty_claim_id.with_context({'call_from_wizard': True}).action_confirm()

