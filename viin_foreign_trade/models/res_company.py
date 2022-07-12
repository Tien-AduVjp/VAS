from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    import_tax_payment_term_id = fields.Many2one('account.payment.term',
                                              string='Default Import Tax Payment Term')

    export_tax_payment_term_id = fields.Many2one('account.payment.term',
                                              string='Default Export Tax Payment Term')

    account_journal_custom_clearance = fields.Many2one('account.journal',
                                                       string='Default Custom Clearance Journal')

    imp_custom_dec_sequence_id = fields.Many2one('ir.sequence',
                                                       string='Custom Declaration Sequence - Import',
                                                       help='The sequence to be used as the internal document number for Custom Declaration - Import')

    exp_custom_dec_sequence_id = fields.Many2one('ir.sequence',
                                                       string='Custom Declaration Sequence - Export',
                                                       help='The sequence to be used as the internal document number for Custom Declaration - Export')

    landed_cost_journal_id = fields.Many2one('account.journal', string='Landed Cost Journal')


    def create_landed_cost_journal_if_not_exists(self):
        self.ensure_one()
        Journal = self.env['account.journal']
        journal_id = Journal.search([('code', '=', 'ITLC'), ('company_id', '=', self.id)])
        if not journal_id:
            journal_id = Journal.create(self._prepare_landed_cost_journal_data())
        self.write({'landed_cost_journal_id': journal_id.id})
        return journal_id

    def _prepare_landed_cost_journal_data(self):
        return {
            'name': _('Default Landed Cost Journal'),
            'code': 'ITLC',
            'type': 'general',
            'company_id': self.id,
            'show_on_dashboard': False,
            }

    @api.model
    def create(self, vals):
        res = super(ResCompany, self).create(vals)
        res.write({
            'imp_custom_dec_sequence_id': res.create_customdec_imp_sequence().id,
            'exp_custom_dec_sequence_id': res.create_customdec_exp_sequence().id,
            })
        return res

    @api.model
    def create_customdec_imp_sequence(self, prefix='CD/IMP/'):
        """
        Create if not exists
        """
        IrSequence = self.env['ir.sequence']
        imp_custom_dec_sequence_id = IrSequence.search([('code', '=', 'custom.declaration.import'), ('company_id', '=', self.id)], limit=1)
        if not imp_custom_dec_sequence_id:
            imp_custom_dec_sequence_id = IrSequence.create({
                'name': self.name + _(': Custom Declaration - Import'),
                'code': 'custom.declaration.import',
                'prefix': prefix,
                'padding': 5,
                'number_next': 1,
                'number_increment': 1,
                'company_id': self.id,
                })
        return imp_custom_dec_sequence_id

    @api.model
    def create_customdec_exp_sequence(self, prefix='CD/EXP/'):
        """
        Create if not exists
        """
        IrSequence = self.env['ir.sequence']
        exp_custom_dec_sequence_id = IrSequence.search([('code', '=', 'custom.declaration.export'), ('company_id', '=', self.id)], limit=1)
        if not exp_custom_dec_sequence_id:
            exp_custom_dec_sequence_id = IrSequence.create({
                'name': self.name + _(': Custom Declaration - Export'),
                'code': 'custom.declaration.export',
                'prefix': prefix,
                'padding': 5,
                'number_next': 1,
                'number_increment': 1,
                'company_id': self.id,
                })
        return exp_custom_dec_sequence_id

    @api.model
    def create_custom_dec_sequences(self):
        """
        Create custom declaration sequence for all existing companies
        """
        for company in self.search([]):
            vals = {}
            if not company.imp_custom_dec_sequence_id:
                vals['imp_custom_dec_sequence_id'] = company.create_customdec_imp_sequence().id
            if not company.imp_custom_dec_sequence_id:
                vals['exp_custom_dec_sequence_id'] = company.create_customdec_exp_sequence().id
            if bool(vals):
                company.write(vals)

    def _prepare_imex_tax_journal_data(self):
        return {
            'name': _('Import/Export Taxes Journal'),
            'code': 'CDJ',
            'type': 'general',
            'company_id': self.id,
            'show_on_dashboard': False,
            }
