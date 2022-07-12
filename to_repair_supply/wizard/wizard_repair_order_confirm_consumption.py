from odoo import models, fields

class WizardRepairOrderConfirmConsumption(models.TransientModel):
    _name = 'wizard.repair.order.confirm.consumption'
    _description = 'Repair Order Confirm Consumption Wizard'

    repair_id = fields.Many2one('repair.order', string='Repair Order')

    def process_with_consumption(self):
        self.ensure_one()
        self.repair_id.with_context(check_consumption=False).action_repair_end()

    def process_without_consumption(self):
        self.ensure_one()
        self.repair_id.with_context(check_consumption=False, without_consumption=True).action_repair_end()
