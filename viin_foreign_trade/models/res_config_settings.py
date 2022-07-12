from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    import_tax_payment_term_id = fields.Many2one('account.payment.term',
                                              string='Default Import Tax Payment Term',
                                              related='company_id.import_tax_payment_term_id', readonly=False,
                                              help='The default payment term applied to importing tax which will be'
                                              ' filled automatically when you working on custom clearance documents.')

    export_tax_payment_term_id = fields.Many2one('account.payment.term',
                                              string='Default Export Tax Payment Term',
                                              related='company_id.export_tax_payment_term_id', readonly=False,
                                              help='The default payment term applied to exporting tax which will be'
                                              ' filled automatically when you working on custom clearance documents.')

    account_journal_custom_clearance = fields.Many2one('account.journal',
                                                       string='Default Custom Clearance Journal',
                                                       related='company_id.account_journal_custom_clearance', readonly=False,
                                                       help='The default account journal to record all accounting transactions'
                                                       ' (taxes) during custom clearance')

    imp_custom_dec_sequence_id = fields.Many2one('ir.sequence',
                                                       string='Custom Declaration Sequence - Import',
                                                       related='company_id.imp_custom_dec_sequence_id', readonly=False,
                                                       help='The sequence to be used as the internal document number for Custom Declaration - Import')

    exp_custom_dec_sequence_id = fields.Many2one('ir.sequence',
                                                       string='Custom Declaration Sequence - Export',
                                                       related='company_id.exp_custom_dec_sequence_id', readonly=False,
                                                       help='The sequence to be used as the internal document number for Custom Declaration - Export')

    landed_cost_journal_id = fields.Many2one('account.journal', related='company_id.landed_cost_journal_id', readonly=False)
