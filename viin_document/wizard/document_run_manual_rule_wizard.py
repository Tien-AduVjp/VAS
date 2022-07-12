from odoo import fields, models

class RunManualRuleWizard(models.TransientModel):
    _name = 'document.run.manual.rule.wizard'
    _description = "Document Run Manual Rule Wizard"

    rule_id = fields.Many2one('document.auto.generate.rule', string="Document Generate Rule", required=True, readonly=True)

    def action_run_manual(self):
        self.ensure_one()
        return self.rule_id.run_manual()
