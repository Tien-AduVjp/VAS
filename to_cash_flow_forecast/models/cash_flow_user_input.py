from odoo import fields, models, api

class CashFlowUserInput(models.Model):
    _name = 'cash.flow.user.input'
    _description = 'Cash Flow User Input'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Short Summary', index=True, required=True)
    type = fields.Selection([('cash_in', 'Cash In'), ('cash_out', 'Cash Out')], string='Type', index=True, required=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True)
    note = fields.Text(string='Note')
    date = fields.Date(string='Date', index=True, required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', index=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('cancel', 'Canceled')], string='State', index=True, default='draft')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    def action_confirm(self):
        self.write({'state': 'confirm'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    def action_cancel(self):
        self.write({'state': 'cancel'})
